"""
just a helper script for testing proxies
"""
import asyncio
import re
import sys

import proxy_utils
from checkers.base_checker import BaseChecker
from models import Proxy
from proxy_py import settings

proxy_find_regex = (
    r"([0-9]{1,3})[^0-9]+([0-9]{1,3})[^0-9]+([0-9]{1,3})[^0-9]+([0-9]{1,3})"
    r"[^0-9]+([0-9]{1,5})"
)
semaphore = asyncio.BoundedSemaphore(settings.NUMBER_OF_CONCURRENT_TASKS)
tasks = []


async def check_task(ip, port):
    async with semaphore:
        for raw_protocol in range(len(Proxy.PROTOCOLS)):
            proxy_url = "{}://{}:{}".format(Proxy.PROTOCOLS[raw_protocol], ip, port)
            check_result, _ = await proxy_utils.check_proxy(proxy_url)
            if check_result:
                break
        # if check_result:
        #     print('proxy {} works'.format(proxy_url))
        print("+" if check_result else "-", end="", file=sys.stderr)
        sys.stderr.flush()


async def main():
    for line in sys.stdin:
        line = line.strip()
        try:
            groups = re.search(proxy_find_regex, line).groups()
        except:
            continue
        ip = ".".join(groups[:4])
        port = groups[4]

        tasks.append(asyncio.ensure_future(check_task(ip, port)))

    await asyncio.gather(*tasks)
    print()
    BaseChecker.clean()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
