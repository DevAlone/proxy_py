import aiohttp

from .base_checker import BaseChecker, CheckerResult


class GoogleComChecker(BaseChecker):
    def __init__(self, timeout=None):
        super(GoogleComChecker, self).__init__("https://www.google.com/humans.txt", timeout=timeout)

    async def validate(self, response: aiohttp.ClientResponse, checker_result: CheckerResult):
        '''
        We have already done the request and it was successful,
        Google returned something(maybe good response, maybe captcha, we don't care)
        '''
        return True
