import collectors_list
import proxy_utils

from proxy_py import settings
from models import Proxy
from models import CollectorState
from models import session
from models import get_or_create

import sqlalchemy
import sqlalchemy.exc
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
        # self.collectors = {}

        # TODO: find better logger
        self.logger = logging.getLogger('proxy_py/processor')
        self.logger.setLevel(logging.DEBUG)
        error_file_handler = logging.FileHandler('logs/processor.error.log')
        error_file_handler.setLevel(logging.ERROR)
        warning_file_handler = logging.FileHandler('logs/processor.warning.log')
        warning_file_handler.setLevel(logging.WARNING)
        info_file_handler = logging.FileHandler('logs/processor.log')
        info_file_handler.setLevel(logging.INFO)

        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(warning_file_handler)
        self.logger.addHandler(info_file_handler)
        if settings.DEBUG:
            debug_file_handler = logging.FileHandler('logs/processor.debug.log')
            debug_file_handler.setLevel(logging.DEBUG)
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

        self.queue = asyncio.Queue(maxsize=settings.PROXY_QUEUE_SIZE)

    async def exec(self):
        await asyncio.wait([
            self.producer(),
            self.consumer(),
        ])

    async def consumer(self):
        tasks = []
        while True:
            await asyncio.sleep(0.1)
            i = 0
            while not self.queue.empty() and i <= settings.CONCURRENT_TASKS_COUNT:
                proxy_data = self.queue.get_nowait()
                tasks.append(self.process_proxy(*proxy_data))
                self.queue.task_done()

            if tasks:
                await asyncio.wait(tasks)
                tasks.clear()

    async def producer(self):
        while True:
            await asyncio.sleep(0.1)
            print("main loop")
            try:
                tasks = []
                for collector_state in session.query(CollectorState) \
                        .filter(CollectorState.last_processing_time < time.time() - CollectorState.processing_period):
                    tasks.append(self.process_collector_of_state(collector_state))

                if tasks:
                    await asyncio.wait(tasks)
                    tasks.clear()

                print("collectors queue size: {}".format(self.queue.qsize()))

                # check proxies

                # check good proxies
                for proxy in session.query(Proxy) \
                        .filter(Proxy.number_of_bad_checks == 0) \
                        .filter(Proxy.last_check_time < time.time() - Proxy.checking_period):
                    await self.add_proxy_to_queue(proxy)

                # check bad proxies
                for proxy in session.query(Proxy) \
                        .filter(Proxy.number_of_bad_checks > 0) \
                        .filter(Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD) \
                        .filter(Proxy.last_check_time < time.time() - settings.BAD_PROXY_CHECKING_PERIOD):
                    await self.add_proxy_to_queue(proxy)

                # check dead proxies
                for proxy in session.query(Proxy) \
                        .filter(Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD) \
                        .filter(Proxy.last_check_time < time.time() - settings.DEAD_PROXY_CHECKING_PERIOD):
                    await self.add_proxy_to_queue(proxy)

                print("queue size: {}".format(self.queue.qsize()))

                await self.queue.join()
            except KeyboardInterrupt as ex:
                raise ex
            except BaseException as ex:
                self.logger.exception(ex)
                await asyncio.sleep(1)

    async def add_proxy_to_queue(self, proxy: Proxy):
        await self.queue.put((
            proxy.get_raw_protocol(),
            proxy.auth_data,
            proxy.domain,
            proxy.port,
            None
        ))

    async def process_collector_of_state(self, collector_state):
        proxies = set()

        collector = await collectors_list.load_collector(collector_state)
        try:
            self.logger.debug('start processing collector of type "' + str(type(collector)) + '"')
            for proxy in (await collector.collect()):
                proxies.add(proxy)

            if len(proxies) == 0:
                self.collector_logger.warning('got 0 proxies from collector of type {}'.format(type(collector)))
            else:
                self.logger.debug('got {0} proxies from collector of type {1}'.format(len(proxies), type(collector)))
                await self.process_raw_proxies(proxies, collector_state.id)
        except KeyboardInterrupt as ex:
            raise ex
        except BaseException as ex:
            self.collector_logger.error("Error in collector of type {}".format(collector_state.identifier))
            self.collector_logger.exception(ex)
        finally:
            collector.last_processing_time = int(time.time())
            await collector.save_state(collector_state)
            collector_state.last_processing_proxies_count = len(proxies)
            # TODO: save new proxies count
            session.commit()

    # TODO: add proxy with domains
    # TODO: add proxy with authorization
    async def process_raw_proxies(self, proxies, collector_id):
        for proxy in proxies:
            self.logger.debug('adding raw proxy {0} to queue'.format(proxy))
            matches = re.match(PROXY_VALIDATE_REGEX, proxy)
            if matches:
                matches = matches.groupdict()
                # protocol = matches['protocol']
                auth_data = matches['auth_data']
                domain = matches['domain']
                port = matches['port']

                if auth_data is None:
                    auth_data = ""

                if domain is None or port is None:
                    raise Exception("Bad raw proxy: {}".format(proxy))

                for i in range(len(Proxy.PROTOCOLS)):
                    await self.queue.put((
                        i,
                        auth_data,
                        domain,
                        port,
                        collector_id,
                    ))

    async def process_proxy(self, raw_protocol: int, auth_data: str, domain: str, port: int, collector_id: int):
        self.logger.debug("start processing proxy {}://{}@{}:{} with collector id {}".format(
            raw_protocol, auth_data, domain, port, collector_id))

        if auth_data is None:
            auth_data = ""

        proxy_url = "{}://".format(Proxy.PROTOCOLS[raw_protocol])
        if auth_data:
            proxy_url += auth_data + "@"

        proxy_url += domain + ":" + str(port)

        try:
            start_checking_time = time.time()
            check_result = await proxy_utils.check_proxy(proxy_url)
            end_checking_time = time.time()

            if check_result:
                self.logger.debug('proxy {0} works'.format(proxy_url))
                self.create_or_update_proxy(
                    raw_protocol,
                    auth_data,
                    domain,
                    port,
                    start_checking_time,
                    end_checking_time
                )
            else:
                self.logger.debug("proxy {0} doesn't work".format(proxy_url))
                proxy = session.query(Proxy).filter(sqlalchemy.and_(
                    Proxy.raw_protocol == raw_protocol,
                    Proxy.auth_data == auth_data,
                    Proxy.domain == domain,
                    Proxy.port == port
                )).first()

                if proxy:
                    proxy.number_of_bad_checks += 1
                    proxy.uptime = int(time.time())

                    if proxy.number_of_bad_checks > settings.REMOVE_ON_N_BAD_CHECKS:
                        self.logger.debug('removing proxy {0} permanently...'.format(proxy.to_url()))
                        session.delete(proxy)

            session.commit()
        except KeyboardInterrupt as ex:
            session.rollback()
            raise ex
        except BaseException as ex:
            session.rollback()
            self.logger.error("Error during processing proxy")
            self.logger.exception(ex)

    @staticmethod
    def create_or_update_proxy(raw_protocol: Proxy.PROTOCOLS, auth_data, domain, port,
                               start_checking_time, end_checking_time):
        if raw_protocol is None or domain is None or port is None or auth_data is None or start_checking_time is None\
                or end_checking_time is None:
            raise Exception("Bad arguments")

        if raw_protocol < 0 or raw_protocol >= len(Proxy.PROTOCOLS):
            raise Exception("Bad protocol")

        response_time = int(round((end_checking_time - start_checking_time) * 1000000))

        proxy = session.query(Proxy).filter(sqlalchemy.and_(
            Proxy.raw_protocol == raw_protocol,
            Proxy.auth_data == auth_data,
            Proxy.domain == domain,
            Proxy.port == port
        )).first()

        if proxy:
            # exists, so update
            pass
        else:
            # doesn't exist, so create
            proxy = Proxy(raw_protocol=raw_protocol, auth_data=auth_data, domain=domain, port=port)
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
