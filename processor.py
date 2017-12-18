import sqlalchemy
from websocket._http import proxy_info

from proxy_py import settings
from models import Proxy
from models import session

import proxy_utils

import asyncio
import time
import re
import logging


# TODO: add ipv6 addresses
PROXY_VALIDATE_REGEX = r"^((?P<protocol>(http|socks4|socks5))://)?" \
                       r"((?P<auth_data>[a-zA-Z0-9_\.]+:[a-zA-Z0-9_\.]+)@)?" \
                       r"(?P<domain>([0-9]{1,3}\.){3}[0-9]{1,3}|([a-zA-Z0-9_]+\.)+[a-zA-Z]+):(?P<port>[0-9]{1,5})/?$"


class Processor:
    """
    main class which collects proxies from collectors, checks them and saves in database
    """

    def __init__(self):
        self.collectors = {}
        # TODO: find better logger
        self.logger = logging.getLogger('proxy_py/processor')
        self.logger.setLevel(logging.DEBUG)
        error_file_handler = logging.FileHandler('logs/processor.error.log')
        error_file_handler.setLevel(logging.ERROR)
        warning_file_handler = logging.FileHandler('logs/processor.warning.log')
        warning_file_handler.setLevel(logging.WARNING)
        info_file_handler = logging.FileHandler('logs/processor.log')
        info_file_handler.setLevel(logging.INFO)
        if settings.DEBUG:
            debug_file_handler = logging.FileHandler('logs/processor.debug.log')
            debug_file_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(warning_file_handler)
        self.logger.addHandler(info_file_handler)
        if settings.DEBUG:
            self.logger.addHandler(debug_file_handler)

        self.collector_logger = logging.getLogger('proxy_py/collectors')
        self.collector_logger.setLevel(logging.WARNING)
        collector_logger_error_file_handler = logging.FileHandler('logs/collectors.error.log')
        collector_logger_error_file_handler.setLevel(logging.ERROR)
        collector_logger_warning_file_handler = logging.FileHandler('logs/collectors.warning.log')
        collector_logger_warning_file_handler.setLevel(logging.WARNING)

        self.collector_logger.addHandler(collector_logger_error_file_handler)
        self.collector_logger.addHandler(collector_logger_warning_file_handler)

        self.logger.debug('processor initialization...')

    async def exec(self, killer):
        while not killer.kill:
            await asyncio.sleep(0.1)
            try:
                tasks = []
                for collector in list(self.collectors.values()):
                    if time.time() >= collector.last_processing_time + collector.processing_period:
                        collector.last_processing_time = int(time.time())
                        tasks.append(asyncio.ensure_future(self._process_collector(collector)))

                if len(tasks) > 0:
                    await asyncio.wait(tasks)
                    tasks.clear()

                # check proxies

                for proxy in session.query(Proxy).all():
                    if time.time() >= proxy.last_check_time + \
                            (settings.BAD_PROXY_CHECKING_PERIOD if proxy.bad_proxy else settings.PROXY_CHECKING_PERIOD):
                        proxy.last_check_time = time.time()
                        tasks.append(asyncio.ensure_future(self._process_proxy(proxy)))
                        if len(tasks) > 500:
                            await asyncio.wait(tasks)
                            tasks.clear()

                if len(tasks) > 0:
                    await asyncio.wait(tasks)
                    tasks.clear()

            except KeyboardInterrupt as ex:
                raise ex;
            except Exception as ex:
                self.logger.exception(ex)
                exit(1)

    async def _process_collector(self, collector):
        try:
            self.logger.debug('start processing collector of type "' + str(type(collector)) + '"')
            proxies = await collector.collect()
            if len(proxies) == 0:
                self.collector_logger.warning('got 0 proxies from collector of type {}'.format(type(collector)))
            else:
                self.logger.debug('got {0} proxies from collector of type {1}'.format(len(proxies), type(collector)))
                await self.process_raw_proxies(proxies)
        except KeyboardInterrupt as ex:
            raise ex;
        except Exception as ex:
            self.collector_logger.error("Error in collector of type {}".format(type(collector)))
            self.collector_logger.exception(ex)
        finally:
            collector.last_processing_time = int(time.time())

    async def _process_proxy(self, proxy: Proxy):
        try:
            self.logger.debug('start processing proxy {0}'.format(proxy.to_url()))
            start_checking_time = time.time()
            check_result = await proxy_utils.check_proxy(proxy)
            end_checking_time = time.time()

            proxy.response_time = int(round((end_checking_time - start_checking_time) * 1000000))

            if check_result:
                self.logger.debug('proxy {0} works'.format(proxy.to_url()))
                proxy.number_of_bad_checks = 0
                if proxy.bad_proxy or proxy.uptime == 0:
                    proxy.uptime = int(time.time())
            else:
                proxy.number_of_bad_checks += 1
                proxy.uptime = int(time.time())

            proxy.last_check_time = int(time.time())

            if proxy.number_of_bad_checks > settings.REMOVE_ON_N_BAD_CHECKS:
                self.logger.debug('removing proxy {0} permanently...'.format(proxy.to_url()))
                session.delete(proxy)

            session.commit()
        except KeyboardInterrupt as ex:
            session.rollback()
            raise ex;
        except Exception as ex:
            session.rollback()
            self.logger.error("Error during processing proxy")
            self.logger.exception(ex)

    def add_collector_of_type(self, CollectorType):
        if CollectorType not in self.collectors:
            self.collectors[CollectorType] = CollectorType()

    def add_proxy(self, protocol: str, domain: str, port: int, auth_data: str = ""):
        if auth_data is None:
            auth_data = ""

        try:
            protocol = Proxy.PROTOCOLS.index(protocol)
        except ValueError:
            self.logger.error("protocol {} of proxy {} {} {} isn't allowed".format(protocol, domain, port, auth_data))
            return

        try:
            proxy = Proxy()
            proxy._protocol = protocol
            proxy.domain = domain
            proxy.port = port
            proxy.auth_data = auth_data

            proxy.uptime = int(time.time())
            proxy.last_check_time = int(time.time())
            self.logger.debug('adding proxy {0}...'.format(proxy.to_url()))
            session.add(proxy)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            self.logger.debug('proxy {} {} {} {} already exists'.format(protocol, domain, port, auth_data))
        except Exception as ex:
            self.logger.exception(ex)
            print('aaaaaaaaaa')
            exit(2)

    # TODO: add proxy with domains
    # TODO: add proxy with authorization
    async def process_raw_proxies(self, proxies):
        tasks = []
        for proxy in proxies:
            self.logger.debug('start processing raw proxy {0}'.format(proxy))
            matches = re.match(PROXY_VALIDATE_REGEX, proxy)
            if matches:
                # await self.process_raw_proxy(**matches.groupdict())
                tasks.append(asyncio.ensure_future(self.process_raw_proxy(**matches.groupdict())))
                if len(tasks) > 500:
                    await asyncio.wait(tasks)
                    tasks.clear()

        if len(tasks) > 0:
            await asyncio.wait(tasks)

    async def process_raw_proxy(self, domain, port, auth_data="", **kwargs):
        proxies = session.query(Proxy).filter_by(domain=domain, port=port, auth_data=auth_data).count()

        if proxies > 0:
            # TODO: remove?
            self.logger.debug('proxy with domain {}, port {} and auth_data {} already exists'.format(
                domain, port, auth_data
            ))
            return

        raw_proxy = ""
        if auth_data is not None:
            raw_proxy += auth_data + "@"

        raw_proxy += "{}:{}".format(domain, port)

        protocols = await proxy_utils.detect_raw_proxy_protocols(raw_proxy)

        if len(protocols) > 0:
            for p in protocols:
                self.add_proxy(p, domain, port, auth_data)
        else:
            self.logger.debug('unable to determine protocol of raw proxy {0}'.format(raw_proxy))


