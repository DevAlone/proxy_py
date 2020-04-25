import aiohttp

from checkers.base_checker import BaseChecker, CheckerResult


class D3DInfoChecker(BaseChecker):
    def __init__(self, timeout=None):
        super(D3DInfoChecker, self).__init__("https://test.d3d.info/ok.html", timeout=timeout)

    async def validate(self, response: aiohttp.ClientResponse, checker_result: CheckerResult):
        return (await response.text()).strip().lower() == 'ok'
