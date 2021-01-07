#!/usr/bin/env python3

# should be called before everything else
# it's very fucking important!
def init_uvloop():
    import uvloop

    uvloop.install()


init_uvloop()

import argparse
import asyncio
import logging
import subprocess
import sys
from statistics import statistics

import collectors_list
import materialized_view_updater
from checkers.base_checker import BaseChecker
from processor import Processor
from proxy_py import settings
from server.proxy_provider_server import ProxyProviderServer
from tools import test_collector

test_collector_path = None
main_logger = None


def process_cmd_arguments():
    global test_collector_path

    def str_to_bool(value):
        if value.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif value.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument(
        "--debug", type=str_to_bool, help="override settings' debug value"
    )
    cmd_parser.add_argument(
        "--proxy-checking-timeout",
        type=float,
        help="override settings' proxy checking timeout",
    )
    cmd_parser.add_argument("--test-collector", help="test collector with a given path")

    args = cmd_parser.parse_args()

    if args.debug is not None:
        settings.DEBUG = args.debug

    if args.proxy_checking_timeout is not None:
        if args.proxy_checking_timeout < 0:
            raise ValueError("--proxy-checking-timeout should be positive")

        settings.PROXY_CHECKING_TIMEOUT = args.proxy_checking_timeout

    test_collector_path = args.test_collector


def prepare_loggers():
    global main_logger

    asyncio_logger = logging.getLogger("asyncio")
    asyncio_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    asyncio_logger_handler = logging.StreamHandler(sys.stdout)
    asyncio_logger_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    asyncio_logger_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_STRING))
    asyncio_logger.addHandler(asyncio_logger_handler)
    asyncio.get_event_loop().set_debug(settings.DEBUG)

    main_logger = logging.getLogger("proxy_py/main")
    main_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    logger_handler = logging.StreamHandler(sys.stdout)
    logger_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_STRING))
    logger_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    main_logger.addHandler(logger_handler)


async def core():
    process_cmd_arguments()
    prepare_loggers()

    if test_collector_path is not None:
        return await test_collector.run(test_collector_path)

    proxy_processor = Processor.get_instance()

    try:
        code = await asyncio.gather(
            *[
                proxy_processor.worker(),
                statistics.worker(),
                materialized_view_updater.worker(),
            ]
        )
        BaseChecker.clean()
        return code
    except KeyboardInterrupt:
        pass
    except BaseException as ex:
        main_logger.exception(ex)
        print("critical error happened, see logs/main.log")
        return 1

    return 0


async def print_collectors():
    for collector_name in collectors_list.collectors.keys():
        print(collector_name)


def server():
    proxy_provider_server = ProxyProviderServer(
        settings.PROXY_PROVIDER_SERVER_ADDRESS["HOST"],
        settings.PROXY_PROVIDER_SERVER_ADDRESS["PORT"],
    )

    return proxy_provider_server.start(asyncio.get_event_loop())


def print_help():
    print(
        """Usage: ./main.py [COMMAND] [OPTION]...
Runs proxy_py

The commands are:

    "core" - runs core part of the project (proxies parsing and processing)
    "print_collectors" - prints collectors
    "server" - runs server for providing API
    "" - runs both

use ./main.py COMMAND --help to get more information

Project's page: https://github.com/DevAlone/proxy_py
"""
    )


def main():
    if len(sys.argv) < 2:
        # run default configuration
        # server
        p = subprocess.Popen(["python3", sys.argv[0], "server"])

        # and core
        code = asyncio.get_event_loop().run_until_complete(core())
        p.wait()
        return code

    command = sys.argv[1].strip()
    sys.argv = sys.argv[1:]
    try:
        return {
            "core": lambda: asyncio.get_event_loop().run_until_complete(core()),
            "print_collectors": lambda: asyncio.get_event_loop().run_until_complete(
                print_collectors()
            ),
            "server": server,
        }[command]()
    except KeyError:
        print_help()
        return 0


if __name__ == "__main__":
    exit(main())
