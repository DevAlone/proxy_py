import sqlalchemy
import sqlalchemy.exc

from async_pool import AsyncPool
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

    async def exec(self):
        pool = AsyncPool(settings.CONCURRENT_TASKS_COUNT)

        while True:
            await asyncio.sleep(0.1)
            print("main loop")
            try:
                # TODO: save collectors' state in database
                # for collector in list(self.collectors.values()):
                #     if time.time() >= collector.last_processing_time + collector.processing_period:
                #         collector.last_processing_time = int(time.time())
                #         await pool.add_task(self._process_collector(collector))

                await pool.wait()

                # check proxies

                # check good proxies
                for proxy in session.query(Proxy)\
                                .filter(Proxy.number_of_bad_checks == 0)\
                                .filter(Proxy.last_check_time < time.time() - Proxy.checking_period):
                    print("good proxies")
                    await pool.add_task(self._process_proxy(proxy))

                # check bad proxies
                for proxy in session.query(Proxy)\
                                .filter(Proxy.number_of_bad_checks > 0)\
                                .filter(Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD)\
                                .filter(Proxy.last_check_time < time.time() - settings.BAD_PROXY_CHECKING_PERIOD):
                    print("bad proxies")
                    await pool.add_task(self._process_proxy(proxy))

                # check dead proxies
                for proxy in session.query(Proxy) \
                        .filter(Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD) \
                        .filter(Proxy.last_check_time < time.time() - settings.DEAD_PROXY_CHECKING_PERIOD):
                    print("dead proxies")
                    await pool.add_task(self._process_proxy(proxy))

                await pool.wait()

            except KeyboardInterrupt as ex:
                raise ex;
            except BaseException as ex:
                self.logger.exception(ex)
                await asyncio.sleep(1)

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
        except BaseException as ex:
            self.collector_logger.error("Error in collector of type {}".format(type(collector)))
            self.collector_logger.exception(ex)
        finally:
            collector.last_processing_time = int(time.time())

    async def _process_proxy(self, proxy: Proxy):
        try:
            self.logger.debug('start processing proxy {0}'.format(proxy.to_url()))

            try:
                start_checking_time = time.time()
                check_result = await proxy_utils.check_proxy(proxy)
                end_checking_time = time.time()
            except:
                raise
            finally:
                proxy.last_check_time = int(time.time())
                session.commit()

            if check_result:
                self.logger.debug('proxy {0} works'.format(proxy.to_url()))
                self.create_or_update_proxy(
                    proxy._protocol,
                    proxy.domain,
                    proxy.port,
                    proxy.auth_data,
                    start_checking_time,
                    end_checking_time
                )
            else:
                self.logger.debug("proxy {0} doesn't work".format(proxy.to_url()))
                proxy.number_of_bad_checks += 1
                proxy.uptime = int(time.time())

                if proxy.number_of_bad_checks > settings.REMOVE_ON_N_BAD_CHECKS:
                    self.logger.debug('removing proxy {0} permanently...'.format(proxy.to_url()))
                    session.delete(proxy)

            session.commit()
        except KeyboardInterrupt as ex:
            session.rollback()
            raise ex;
        except BaseException as ex:
            session.rollback()
            self.logger.error("Error during processing proxy")
            self.logger.exception(ex)

    def add_collector_of_type(self, CollectorType):
        if CollectorType not in self.collectors:
            self.collectors[CollectorType] = CollectorType()

    def create_or_update_proxy(self, _protocol : Proxy.PROTOCOLS, domain, port, auth_data,
                               start_checking_time, end_checking_time):
        if _protocol is None or domain is None or port is None or auth_data is None or start_checking_time is None\
                or end_checking_time is None:
            raise Exception()

        if _protocol < 0 or _protocol >= len(Proxy.PROTOCOLS):
            raise Exception()

        response_time = int(round((end_checking_time - start_checking_time) * 1000000))

        proxy = session.query(Proxy).filter(sqlalchemy.and_(
            Proxy._protocol == _protocol,
            Proxy.auth_data == auth_data,
            Proxy.domain == domain,
            Proxy.port == port
        )).first()

        if proxy:
            # exists, so update
            pass
        else:
            # doesn't exist, so create
            proxy = Proxy(_protocol=_protocol, auth_data=auth_data, domain=domain, port=port)
            session.add(proxy)

        proxy.response_time = response_time
        proxy.number_of_bad_checks = 0
        proxy.last_check_time = int(time.time())

        if proxy.bad_proxy or proxy.uptime is None or proxy.uptime == 0:
            proxy.uptime = int(time.time())

        checking_time = int(end_checking_time - start_checking_time)
        if checking_time > settings.PROXY_CHECKING_TIMEOUT:
            checking_time = settings.PROXY_CHECKING_TIMEOUT

        proxy.checking_period = \
            settings.MIN_PROXY_CHECKING_PERIOD \
            + (checking_time / settings.PROXY_CHECKING_TIMEOUT) \
            * (settings.MAX_PROXY_CHECKING_PERIOD - settings.MIN_PROXY_CHECKING_PERIOD)

        session.commit()

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
                if len(tasks) > 100:
                    await asyncio.wait(tasks)
                    tasks.clear()

        if len(tasks) > 0:
            await asyncio.wait(tasks)

    async def process_raw_proxy(self, domain, port, auth_data="", **kwargs):
        if domain is None or port is None:
            raise Exception()

        if auth_data is None:
            auth_data = ""

        # proxies = session.query(Proxy).filter_by(domain=domain, port=port, auth_data=auth_data).count()
        #
        # if proxies > 0:
        #     # TODO: remove? or maybe check other protocols
        #     self.logger.debug('proxy with domain {}, port {} and auth_data {} already exists'.format(
        #         domain, port, auth_data
        #     ))
        #     return

        proxies = await proxy_utils.get_working_proxies(domain, port, auth_data)

        if len(proxies) > 0:
            for _proxy in proxies:
                proxy = _proxy[0]
                start_checking_time = _proxy[1]
                end_checking_time = _proxy[2]

                self.create_or_update_proxy(
                    proxy._protocol,
                    proxy.domain,
                    proxy.port,
                    proxy.auth_data,
                    start_checking_time,
                    end_checking_time
                )
        else:
            self.logger.debug('unable to determine protocol of raw proxy {} {} {}'.format(domain, port, auth_data))


