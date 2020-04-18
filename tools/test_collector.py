import time

from termcolor import colored
import termcolor
from models import Proxy
from proxy_py import settings
from collectors_list import collectors

import re
import sys
import proxy_utils
import asyncio
import proxy_validator

from parsers.regex_parser import RegexParser


def eprint(*args, **kwargs):
    return print(*args, file=sys.stderr, **kwargs)


PROXIES_PER_TIME = 8192


async def run(path: str):
    path, class_name = path.split(':', maxsplit=2)
    path = re.sub(r"\.py$", "", path).replace('/', '.')
    path += '.' + class_name

    try:
        collector = collectors[path]
    except KeyError:
        eprint("Collector doesn't exist(maybe you forgot to set __collector__ to True)")
        return 1

    total = 0
    result = []

    async for proxy in collector.collect():
        total += 1
        result.append(proxy)

        if len(result) >= PROXIES_PER_TIME:
            print(f"got more than {PROXIES_PER_TIME} proxies, checking this part")
            # await asyncio.gather(*[process_proxy(proxy) for proxy in result])
            result = []

    # await asyncio.gather(*[process_proxy(proxy) for proxy in result])
    print("Total number of proxies: {}".format(total))


proxies_semaphore = asyncio.BoundedSemaphore(settings.NUMBER_OF_CONCURRENT_TASKS)


async def process_proxy(proxy_url: str):
    async with proxies_semaphore:
        try:
            _, auth_data, domain, port = proxy_validator.retrieve(proxy_url)
        except proxy_validator.ValidationError as ex:
            raise ValueError(
                "Your collector returned bad proxy \"{}\". Message: \"{}\"".format(proxy_url, ex)
            )

        is_working = False
        for raw_protocol in range(len(Proxy.PROTOCOLS)):
            proxy_url = "{}://".format(Proxy.PROTOCOLS[raw_protocol])
            if auth_data:
                proxy_url += auth_data + "@"

            proxy_url += domain + ":" + str(port)

            start_checking_time = time.time()
            check_result, checker_additional_info = await proxy_utils.check_proxy(proxy_url)
            end_checking_time = time.time()

            if check_result:
                is_working = True
                break

        response_time = end_checking_time - start_checking_time

        color = ''

        if not is_working:
            color = 'red'
        elif response_time < 1:
            color = 'cyan'
        elif response_time < 5:
            color = 'green'
        elif response_time < 10:
            color = 'yellow'
        else:
            color = 'magenta'

        print(colored(' ', on_color='on_' + color), end='')

        sys.stdout.flush()
