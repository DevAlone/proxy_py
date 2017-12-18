from core.models import Proxy
import proxy_utils

from django.conf import settings


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
        self.logger = logging.getLogger('proxy_py/processor')
        self.logger.setLevel(logging.DEBUG)
        error_file_handler = logging.FileHandler('logs/processor.error.log')
        error_file_handler.setLevel(logging.ERROR)
        warning_file_handler = logging.FileHandler('logs/processor.warning.log')
        warning_file_handler.setLevel(logging.WARNING)
        info_file_handler = logging.FileHandler('processor.log')
        info_file_handler.setLevel(logging.INFO)
        if settings.DEBUG:
            debug_file_handler = logging.FileHandler('logs/processor.debug.log')
            debug_file_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(warning_file_handler)
        self.logger.addHandler(info_file_handler)
        if settings.DEBUG:
            self.logger.addHandler(debug_file_handler)

        self.logger.debug('processor initialization...')

    async def exec(self, killer):
        while not killer.kill:
            try:
                tasks = []
                for collector in list(self.collectors.values()):
                    if time.time() >= collector.last_processing_time + collector.processing_period:
                        collector.last_processing_time = time.time()
                        tasks.append(asyncio.ensure_future(self._process_collector(collector)))

                # check proxies
                for proxy in Proxy.objects.all():
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
                raise ex
            except Exception as ex:
                self.logger.exception(ex)

    async def _process_collector(self, collector):
        try:
            self.logger.debug('start processing collector of type "' + str(type(collector)) + '"')
            proxies = await collector.collect()
            self.logger.debug('got {0} proxies from collector of type {1}'.format(len(proxies), type(collector)))
            await self.process_raw_proxies(proxies)
            collector.last_processing_time = time.time()
        except KeyboardInterrupt as ex:
            raise ex
        except Exception as ex:
            self.logger.error("Error in collector")
            self.logger.exception(ex)

    async def _process_proxy(self, proxy: Proxy):
        try:
            self.logger.debug('start processing proxy {0}'.format(proxy.to_url()))
            check_result = await proxy_utils.check_proxy(proxy)

            if check_result:
                self.logger.debug('proxy {0} works'.format(proxy.to_url()))
                proxy.number_of_bad_checks = 0
                if proxy.bad_proxy or proxy.uptime == 0:
                    proxy.uptime = time.time()
                proxy.bad_proxy = False
            else:
                proxy.number_of_bad_checks += 1
                proxy.uptime = time.time()

            proxy.last_check_time = int(time.time())

            # TODO: move to settings
            if proxy.number_of_bad_checks > 3:
                self.logger.debug('removing proxy {0}...'.format(proxy.to_url()))
                proxy.bad_proxy = True
                if proxy.number_of_bad_checks > 500:
                    self.logger.debug('removing proxy {0} permanently...'.format(proxy.to_url()))
                    proxy.delete()
                    return


            proxy.save()
        except KeyboardInterrupt as ex:
            raise ex
        except Exception as ex:
            self.logger.error("Error during processing proxy")
            self.logger.exception(ex)

    def add_collector_of_type(self, CollectorType):
        if CollectorType not in self.collectors:
            self.collectors[CollectorType] = CollectorType()

    def add_proxy(self, protocol: str, domain: str, port: int, auth_data: str = None):
        try:
            protocol = Proxy.PROTOCOLS.index(protocol)
        except ValueError:
            self.logger.error("protocol {} of proxy {} {} {} isn't allowed".format(protocol, domain, port, auth_data))
            return

        try:
            proxy = Proxy.objects.get(_protocol=protocol, domain=domain, port=port, auth_data=auth_data)
            self.logger.debug('proxy {0} already exists'.format(proxy.to_url()))
        except Proxy.DoesNotExist:
            proxy = Proxy()
            proxy._protocol = protocol
            proxy.domain = domain
            proxy.port = port
            proxy.auth_data = auth_data

            proxy.uptime = time.time()
            proxy.last_check_time = int(time.time())
            proxy.save()
            self.logger.debug('adding proxy {0}...'.format(proxy.to_url()))

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

    async def process_raw_proxy(self, domain, port, protocol=None, auth_data=None):
        proxies = Proxy.objects.filter(domain=domain, port=port, auth_data=auth_data)
        if proxies:
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

