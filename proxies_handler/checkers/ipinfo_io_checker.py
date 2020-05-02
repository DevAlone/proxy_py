from .base_checker import BaseChecker, CheckerResult
import aiohttp


class IPInfoIOChecker(BaseChecker):
    def __init__(self, timeout=None):
        super(IPInfoIOChecker, self).__init__("https://ipinfo.io/json", timeout=timeout)

    async def validate(self, response: aiohttp.ClientResponse, checker_result: CheckerResult) -> bool:
        if response.status != 200:
            return False

        json_result = await response.json()
        if 'ip' in json_result:
            checker_result.ipv4 = json_result['ip']
        if 'city' in json_result:
            checker_result.city = json_result['city']
        if 'region' in json_result:
            checker_result.region = json_result['region']
        if 'country' in json_result:
            checker_result.country_code = json_result['country']
        if 'loc' in json_result:
            checker_result.location_coordinates = tuple(float(x) for x in json_result['loc'].split(','))
        if 'org' in json_result:
            checker_result.organization_name = json_result['org']

        return True
