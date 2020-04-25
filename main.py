#!/usr/bin/env python3
import asyncio
import logging
import sys

import broker
import proxies_handler
import settings
import tasks_handler


async def main() -> int:
    init_logging()

    if len(sys.argv) < 2:
        print("Command is required")
        print()
        print_help()
        return 1

    command = sys.argv[1].strip().lower()
    sys.argv = sys.argv[1:]
    try:
        func = {
            "proxies_handler": proxies_handler.main,
            "tasks_handler": tasks_handler.main,
            "broker": broker.main,
        }[command]

        return await func()
    except KeyError:
        print("Unknown command")
        print_help()
        return 2


help_message = """Usage: ./main.py COMMAND [OPTION]...
Runs proxy_py

The commands are:
// TODO: update
    "core" - runs core part of the project (proxies parsing and processing)
    "print_collectors" - prints collectors
    "server" - runs server for providing API

use ./main.py COMMAND --help to get more information

Project's page: https://github.com/DevAlone/proxy_py
"""


def print_help():
    print(help_message)


def init_logging():
    logging.root.setLevel(settings.log_level)


if __name__ == "__main__":
    exit(asyncio.run(main()))
