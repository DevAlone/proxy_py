from proxy_py import settings
import proxy_utils
import importlib
import importlib.util
import os
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
    file_path = sys.argv[1]
    module_name = os.path.splitext(file_path)[0].replace('/', '.')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    collector_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector_module)

    if not hasattr(collector_module, "Collector") \
            or not hasattr(collector_module.Collector, "__collector__") \
            or not collector_module.Collector.__collector__:
        raise Exception('it is not a collector')

    collector = collector_module.Collector()
    while True:
        proxies = await collector.collect()
        # proxies = await collector.process_page(2)
        # print(proxies)
        tasks = []
        # print(proxies)
        for proxy in proxies:
            print(proxy)
            tasks.append(check_raw_proxy(proxy))

        if tasks:
            await asyncio.gather(*tasks)
        else:
            print("Empty")
        print()

        await asyncio.sleep(5)


if __name__ == '__main__':
    loop.run_until_complete(main())
