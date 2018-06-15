#!/usr/bin/env python3

from proxy_py import settings
from processor import Processor
from server.proxy_provider_server import ProxyProviderServer
from statistics import statistics
from checkers.base_checker import BaseChecker

import asyncio
import logging


if __name__ == "__main__":
    main_logger = logging.getLogger("proxy_py/main")

    if settings.DEBUG:
        main_logger.setLevel(logging.DEBUG)
    else:
        main_logger.setLevel(logging.INFO)

    logger_file_handler = logging.FileHandler("logs/main.log")
    logger_file_handler.setLevel(logging.DEBUG)
    logger_file_handler.setFormatter(
        logging.Formatter(
            "%(levelname)s ~ %(asctime)s ~ %(funcName)30s() ~ %(message)s"
        )
    )

    main_logger.addHandler(logger_file_handler)

    loop = asyncio.get_event_loop()
    # TODO: consider loop.set_debug

    proxy_processor = Processor.get_instance()

    proxy_provider_server = ProxyProviderServer(
        settings.PROXY_PROVIDER_SERVER_ADDRESS['HOST'],
        settings.PROXY_PROVIDER_SERVER_ADDRESS['PORT'],
        proxy_processor,
    )

    loop.run_until_complete(proxy_provider_server.start(loop))

    try:
        loop.run_until_complete(asyncio.gather(*[
            proxy_processor.worker(),
            statistics.worker(),
        ]))
        BaseChecker.clean()
    except BaseException as ex:
        main_logger.exception(ex)
        print("critical error happened, see logs/main.log")
