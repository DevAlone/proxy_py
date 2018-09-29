from checkers.base_checker import CheckerResult
from proxy_py import settings
from models import Proxy, CollectorState, db

import collectors_list
import proxy_utils
import asyncio
import time
import re
import logging
import peewee


# TODO: add ipv6 addresses, make domain checking better
_0_TO_255_REGEX = r"([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
DOMAIN_LETTER_REGEX = r"[a-zA-Z0-9_\-]"
PROXY_VALIDATE_REGEX = \
    r"^((?P<protocol>(http|socks4|socks5))://)?" \
    r"((?P<auth_data>[a-zA-Z0-9_\.]+:[a-zA-Z0-9_\.]+)@)?" \
    r"(?P<domain>" + \
        r"(" + _0_TO_255_REGEX + "\.){3}" + _0_TO_255_REGEX + \
        r"|" + DOMAIN_LETTER_REGEX + r"+(\.[a-zA-Z]" + DOMAIN_LETTER_REGEX + r"+)*):" \
    r"(?P<port>([1-9]|[1-8][0-9]|9[0-9]|[1-8][0-9]{2}|9[0-8][0-9]|99[0-9]|[1-8][0-9]{3}|9[0-8][0-9]{2}|99[0-8][0-9]|999[0-9]|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))/?$"

LOGGERS_FORMAT = "%(levelname)s ~ %(asctime)s ~ %(funcName)30s() ~ %(message)s"


class Processor:
    """
    main class which collects proxies from collectors,
    checks them and saves in database
    """
    instance = None

    @staticmethod
    def get_instance():
        if Processor.instance is None:
            Processor.instance = Processor()

        return Processor.instance

    def __init__(self):
        self.logger = logging.getLogger("proxy_py/processor")

        if settings.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        logger_file_handler = logging.FileHandler("logs/processor.log")
        logger_file_handler.setLevel(logging.DEBUG)
        logger_file_handler.setFormatter(logging.Formatter(LOGGERS_FORMAT))

        self.logger.addHandler(logger_file_handler)

        self.collectors_logger = logging.getLogger("proxy_py/collectors")
        if settings.DEBUG:
            self.collectors_logger.setLevel(logging.DEBUG)
        else:
            self.collectors_logger.setLevel(logging.INFO)

        collectors_logger_file_handler = logging.FileHandler("logs/collectors.log")
        collectors_logger_file_handler.setLevel(logging.DEBUG)
        logger_file_handler.setFormatter(logging.Formatter(LOGGERS_FORMAT))

        self.collectors_logger.addHandler(collectors_logger_file_handler)

        self.logger.debug("processor initialization...")

        self.proxies_semaphore = asyncio.BoundedSemaphore(settings.NUMBER_OF_CONCURRENT_TASKS)
        self.good_proxies_are_processed = False

    async def worker(self):
        await asyncio.gather(*[
            self.process_proxies(),
            self.process_collectors(),
        ])

    async def process_proxies(self):
        while True:
            await asyncio.sleep(0.01)
            try:
                # check good proxies
                proxies = await db.execute(
                    Proxy.select().where(
                        Proxy.number_of_bad_checks == 0,
                        Proxy.last_check_time < time.time() - Proxy.checking_period,
                    ).order_by(Proxy.last_check_time).limit(settings.NUMBER_OF_CONCURRENT_TASKS)
                )
                if proxies:
                    self.good_proxies_are_processed = False

                await self.add_proxies_to_queue(proxies)

                if proxies:
                    continue

                self.good_proxies_are_processed = True

                # check bad proxies
                proxies = await db.execute(
                    Proxy.select().where(
                        Proxy.number_of_bad_checks > 0,
                        Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD,
                        Proxy.last_check_time < time.time() - settings.BAD_PROXY_CHECKING_PERIOD,
                    ).order_by(Proxy.last_check_time).limit(settings.NUMBER_OF_CONCURRENT_TASKS)
                )

                await self.add_proxies_to_queue(proxies)

                if proxies:
                    continue

                # check dead proxies
                proxies = await db.execute(
                    Proxy.select().where(
                        Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD,
                        Proxy.number_of_bad_checks < settings.DO_NOT_CHECK_ON_N_BAD_CHECKS,
                        Proxy.last_check_time < time.time() - settings.DEAD_PROXY_CHECKING_PERIOD,
                    ).order_by(Proxy.last_check_time).limit(settings.NUMBER_OF_CONCURRENT_TASKS)
                )

                await self.add_proxies_to_queue(proxies)
            except KeyboardInterrupt as ex:
                raise ex
            except BaseException as ex:
                self.logger.exception(ex)
                if settings.DEBUG:
                    raise ex

                await asyncio.sleep(settings.SLEEP_AFTER_ERROR_PERIOD)

    async def process_collectors(self):
        while True:
            await asyncio.sleep(0.1)
            try:
                # check collectors
                collector_states = await db.execute(
                    CollectorState.select().where(
                        CollectorState.last_processing_time < time.time() - CollectorState.processing_period
                    ).order_by(peewee.fn.Random()).limit(settings.NUMBER_OF_CONCURRENT_COLLECTORS)
                )

                await asyncio.gather(*[
                    self.process_collector_of_state(collector_state)
                    for collector_state in collector_states
                ])
            except KeyboardInterrupt as ex:
                raise ex
            except BaseException as ex:
                self.collectors_logger.exception(ex)
                if settings.DEBUG:
                    raise ex

                await asyncio.sleep(settings.SLEEP_AFTER_ERROR_PERIOD)

    async def add_proxy_to_queue(self, proxy: Proxy, collector_id=None):
        async with self.proxies_semaphore:
            asyncio.ensure_future(self.process_proxy(
                proxy.get_raw_protocol(),
                proxy.auth_data,
                proxy.domain,
                proxy.port,
                collector_id,
            ))

    async def add_proxies_to_queue(self, proxies: list):
        for proxy in proxies:
            await self.add_proxy_to_queue(proxy)

    async def process_collector_of_state(self, collector_state):
        collector = await collectors_list.load_collector(collector_state)
        try:
            self.logger.debug(
                "start processing collector of type \"{}\"".format(type(collector))
            )
            proxies = await collector._collect()

            if proxies:
                self.logger.debug(
                    "got {} proxies from collector of type \"{}\"".format(len(proxies), type(collector))
                )
                await self.process_raw_proxies(proxies, collector_state.id)
            else:
                self.collectors_logger.warning(
                    "got 0 proxies from collector of type \"{}\"".format(type(collector))
                )
        except KeyboardInterrupt as ex:
            raise ex
        except BaseException as ex:
            self.collectors_logger.error(
                "Error in collector of type \"{}\"".format(collector_state.identifier)
            )
            self.collectors_logger.exception(ex)
        finally:
            collector.last_processing_time = int(time.time())
            # TODO: new proxies count
            await collectors_list.save_collector(collector_state)

    async def process_raw_proxies(self, proxies, collector_id):
        tasks = []

        for proxy in proxies:
            # TODO: refactor it
            tasks.append(self.process_raw_proxy(proxy, collector_id))
            if len(tasks) > settings.NUMBER_OF_CONCURRENT_TASKS:
                await asyncio.gather(*tasks)
                tasks.clear()

        if tasks:
            await asyncio.gather(*tasks)

    async def process_raw_proxy(self, proxy, collector_id):
        self.logger.debug("processing raw proxy \"{}\"".format(proxy))

        matches = re.match(PROXY_VALIDATE_REGEX, proxy)
        if matches:
            matches = matches.groupdict()
            auth_data = matches["auth_data"]
            domain = matches["domain"]
            port = matches["port"]

            if auth_data is None:
                auth_data = ""

            if domain is None or port is None:
                self.collectors_logger.error(
                    "Bad raw proxy \"{}\" from collector \"{}\"".format(proxy, collector_id)
                )
                return

            # don't care about protocol
            try:
                proxy = await db.get(
                    Proxy.select().where(
                        Proxy.auth_data == auth_data,
                        Proxy.domain == domain,
                        Proxy.port == port,
                    )
                )

                if proxy.last_check_time + settings.PROXY_NOT_CHECKING_PERIOD >= time.time():
                    proxy_short_address = ""
                    if auth_data:
                        proxy_short_address += auth_data + "@"

                    proxy_short_address += "{}:{}".format(domain, port)

                    self.logger.debug(
                        "skipping proxy \"{}\" from collector \"{}\"".format(
                            proxy_short_address, collector_id)
                    )
                    return
            except Proxy.DoesNotExist:
                pass

            for raw_protocol in range(len(Proxy.PROTOCOLS)):
                while not self.good_proxies_are_processed:
                    # TODO: find a better way
                    await asyncio.sleep(0.1)

                new_proxy = Proxy()
                new_proxy.raw_protocol = raw_protocol
                new_proxy.auth_data = auth_data
                new_proxy.domain = domain
                new_proxy.port = port

                await self.add_proxy_to_queue(new_proxy, collector_id)

    async def process_proxy(self, raw_protocol: int, auth_data: str, domain: str, port: int, collector_id):
        async with self.proxies_semaphore:
            self.logger.debug(
                "start processing proxy {}://{}@{}:{} with collector id {}".format(
                    raw_protocol, auth_data, domain, port, collector_id)
            )

            if auth_data is None:
                auth_data = ""

            proxy_url = "{}://".format(Proxy.PROTOCOLS[raw_protocol])
            if auth_data:
                proxy_url += auth_data + "@"

            proxy_url += domain + ":" + str(port)

            start_checking_time = time.time()
            check_result, checker_additional_info = await proxy_utils.check_proxy(proxy_url)
            end_checking_time = time.time()

            if check_result:
                self.logger.debug("proxy {0} works".format(proxy_url))
                await self.create_or_update_proxy(
                    raw_protocol,
                    auth_data,
                    domain,
                    port,
                    start_checking_time,
                    end_checking_time,
                    checker_additional_info
                )
            else:
                self.logger.debug("proxy {0} doesn't work".format(proxy_url))
                try:
                    proxy = await db.get(
                        Proxy.select().where(
                            Proxy.raw_protocol == raw_protocol,
                            Proxy.auth_data == auth_data,
                            Proxy.domain == domain,
                            Proxy.port == port,
                        )
                    )

                    proxy.last_check_time = int(time.time())
                    proxy.number_of_bad_checks += 1
                    proxy.uptime = int(time.time())

                    if proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD:
                        proxy.bad_uptime = int(time.time())

                    if proxy.number_of_bad_checks == settings.DO_NOT_CHECK_ON_N_BAD_CHECKS:
                        self.logger.debug("proxy {} isn't checked anymore".format(proxy.to_url()))

                    await db.update(proxy)
                except Proxy.DoesNotExist:
                    pass

    @staticmethod
    async def create_or_update_proxy(
        raw_protocol: Proxy.PROTOCOLS,
        auth_data: str,
        domain: str,
        port: int,
        start_checking_time: int,
        end_checking_time: int,
        additional_info: CheckerResult
    ):
        if raw_protocol is None or domain is None or port is None or auth_data is None or start_checking_time is None\
                or end_checking_time is None:
            raise ValueError("Processor.create_or_update_proxy: Bad arguments")

        if raw_protocol < 0 or raw_protocol >= len(Proxy.PROTOCOLS):
            raise ValueError("Processor.create_or_update_proxy: Bad protocol")

        # to microseconds
        response_time = int(round((end_checking_time - start_checking_time) * 1000000))

        async with db.atomic():
            # TODO: fix spontaneous issue with unique constraint:
            # peewee.IntegrityError: duplicate key value violates unique constraint
            # "proxies_raw_protocol_auth_data_domain_port"

            proxy, was_created = await db.get_or_create(
                Proxy,
                raw_protocol=raw_protocol,
                auth_data=auth_data,
                domain=domain,
                port=port,
            )

            if was_created:
                proxy.number_of_bad_checks = 0

            if proxy.bad_proxy or proxy.uptime is None or proxy.uptime == 0:
                proxy.uptime = int(time.time())

            if proxy.bad_uptime is None or proxy.bad_uptime == 0 or \
                    proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD:
                proxy.bad_uptime = int(time.time())

            proxy.response_time = response_time
            proxy.number_of_bad_checks = 0
            proxy.last_check_time = int(time.time())

            if additional_info is not None:
                if additional_info.ipv4 is not None:
                    proxy.white_ipv4 = additional_info.ipv4

                if additional_info.city is not None:
                    proxy.city = additional_info.city

                if additional_info.region is not None:
                    proxy.region = additional_info.region

                if additional_info.country_code is not None:
                    proxy.country_code = additional_info.country_code.strip().lower()

            checking_time = int(end_checking_time - start_checking_time)
            if checking_time > settings.PROXY_CHECKING_TIMEOUT:
                checking_time = settings.PROXY_CHECKING_TIMEOUT

            proxy.checking_period = settings.MIN_PROXY_CHECKING_PERIOD \
                + (checking_time / settings.PROXY_CHECKING_TIMEOUT) \
                * (settings.MAX_PROXY_CHECKING_PERIOD - settings.MIN_PROXY_CHECKING_PERIOD)

            await db.update(proxy)
