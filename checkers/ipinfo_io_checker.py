from checkers.base_checker import BaseChecker, CheckerResult

import aiohttp


class IPInfoIOChecker(BaseChecker):
    def __init__(self, timeout=10):
        super(IPInfoIOChecker, self).__init__("https://ipinfo.io/json", timeout=timeout)

    async def _check(self, response: aiohttp.ClientResponse, checker_result: CheckerResult) -> bool:
        if response.status != 200:
            return False

        json_result = await response.json()
        checker_result.ipv4 = json_result['ip']
        checker_result.city = json_result['city']
        checker_result.region = json_result['region']
        checker_result.country_code = json_result['country']
        checker_result.location_coordinates = tuple(float(x) for x in json_result['loc'].split(','))
        checker_result.organization_name = json_result['org']

        return True
