import aiohttp

from checkers.base_checker import BaseChecker, CheckerResult


class D3DInfoChecker(BaseChecker):
    def __init__(self, timeout=None):
        super(D3DInfoChecker, self).__init__("https://pikagraphs.d3d.info/OK/", timeout=timeout)

    async def _check(self, response: aiohttp.ClientResponse, checker_result: CheckerResult):
        return (await response.text()) == 'OK'
