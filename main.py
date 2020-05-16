#!/usr/bin/env python3

import asyncio
import logging
import sys
import typing

from termcolor import colored

import settings
import commands
from commands import commands_dict


def main() -> int:
    init_logging()

    if len(sys.argv) < 2:
        print(colored("Command is required", "red"))
        print()
        commands.print_help()
        return 1

    command = sys.argv[1].strip().lower().replace("_", "-")
    sys.argv = sys.argv[1:]
    try:
        func: typing.Any = commands_dict[command][0]

        if asyncio.iscoroutinefunction(func):
            return asyncio.run(func())

        return func()
    except KeyError:
        print(colored("Unknown command", "red"))
        print()
        commands.print_help()
        return 2


def init_logging():
    logging.root.setLevel(settings.log_level)
    formatter = logging.Formatter(settings.log_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)


if __name__ == "__main__":
    exit(main())
