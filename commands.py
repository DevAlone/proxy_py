from termcolor import colored

import collectors_handler
import proxies_handler
import results_handler
import server
import tasks_handler


def print_help():
    commands_str = ""
    for command_name, items in commands_dict.items():
        _, command_description = items
        commands_str += f'\t{colored(command_name, "green")} {command_description}\n'

    print(f"""Usage: ./main.py COMMAND [OPTION]...

Runs proxy_py

The commands are:

{commands_str}

use ./main.py COMMAND --help to get more information

Project's page: https://github.com/DevAlone/proxy_py
    """)


def print_version():
    print(f"libzmq version is\t{zmq.zmq_version()}")
    print(f"pyzmq version is\t{zmq.__version__}")


commands_dict = {
    "collectors-handler": (collectors_handler.main, "runs collectors handler"),
    "proxies-handler": (proxies_handler.main, "runs proxies_handler"),
    "tasks-handler": (tasks_handler.main, "runs tasks handler"),
    "results-handler": (results_handler.main, "runs results handler"),
    "server": (server.main, "runs server"),
    "print-version": (print_version, "prints version"),
    "version": (print_version, "prints version"),
    "--version": (print_version, "prints version"),
    "-v": (print_version, "prints version"),
    "print-help": (print_help, "prints help"),
    "--help": (print_help, "prints help"),
    "-h": (print_help, "prints help"),
}
