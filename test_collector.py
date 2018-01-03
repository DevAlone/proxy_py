from collectors.freeproxylists_net.freeproxylists_net import Collector

import proxy_utils

import asyncio
import sys


loop = asyncio.get_event_loop()


async def check_raw_proxy(raw_proxy: str):
    protocols = [
        "http", "socks4", "socks5"
    ]
    works = False
    for protocol in protocols:
        # print("checking... {}".format(raw_proxy))
        result = await proxy_utils.check_proxy("{}://{}".format(protocol, raw_proxy), timeout=5)
        if result:
            works = True
            break

    print("1" if works else "0", end="")
    sys.stdout.flush()

    return works


async def main():
    collector = Collector()
    while True:
        proxies = await collector.collect()
        # print(proxies)
        tasks = []
        # print(proxies)
        for proxy in proxies:
            tasks.append(check_raw_proxy(proxy))

        if tasks:
            await asyncio.wait(tasks)
        else:
            print("Empty")
        print()

        await asyncio.sleep(5)


if __name__ == '__main__':
    loop.run_until_complete(main())
