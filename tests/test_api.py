import asyncio
import aiohttp
import json


API_URL = "http://localhost:55555"


async def get_proxies(session, request):
    async with session.post(API_URL, json=request) as resp:
        json_data = json.loads(await resp.text())
        return json_data['data']


async def test_ordering(session, field_name):
    request_data = {
        'method': 'get',
        'model': 'proxy',
        'order_by': field_name
    }

    previous_proxy = None

    for proxy in await get_proxies(session, request_data):
        if previous_proxy is not None:
            if previous_proxy[field_name] > proxy[field_name]:
                return False

        previous_proxy = proxy

    return True


async def test_complex_ordering(session, *args):
    fields = args

    request_data = {
        'method': 'get',
        'model': 'proxy',
        'order_by': ', '.join(fields)
    }

    previous_proxy = None

    for proxy in await get_proxies(session, request_data):
        if previous_proxy is not None:
            for i in range(1, len(fields)):
                previous_field = fields[i - 1]
                field = fields[i]

                if previous_proxy[previous_field] > proxy[previous_field]:
                    return False
                elif previous_proxy[previous_field] < proxy[previous_field]:
                    break

        previous_proxy = proxy

    return True


async def run_tests(session):
    tests = [
        (test_ordering, 'response_time'),
        (test_ordering, 'uptime'),
        (test_ordering, 'number_of_bad_checks'),
        (test_ordering, 'last_check_time'),
        (test_complex_ordering, 'uptime', 'last_check_time'),
        (test_complex_ordering, 'number_of_bad_checks', 'uptime', 'response_time'),
    ]

    for test in tests:
        try:
            result = await test[0](session, *test[1:])
            print("PASSED" if result else "FAILED", end='')
        except BaseException as ex:
            print("FAILED DUE TO EXCEPTION: {}".format(ex), end='')
        finally:
            print(" test {} ".format(test))


async def main():
    async with aiohttp.ClientSession() as session:
        await run_tests(session)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
