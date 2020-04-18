from aiosocks.connector import ProxyConnector, ProxyClientRequest
from proxy_py import settings

import ssl
import aiohttp
import aiosocks
import asyncio
import async_requests


class CheckerResult:
    # TODO: change to properties with validation
    ipv4 = None
    ipv6 = None
    city = None
    region = None
    country_code = None
    # tuple
    location_coordinates = None
    organization_name = None

    def update_from_other(self, other):
        def set_attr_if_is_not_none(attribute_name, first_obj, second_obj):
            if hasattr(second_obj, attribute_name):
                second_val = getattr(second_obj, attribute_name)
                setattr(first_obj, attribute_name, second_val)

        set_attr_if_is_not_none("ipv4", self, other)
        set_attr_if_is_not_none("ipv6", self, other)
        set_attr_if_is_not_none("city", self, other)
        set_attr_if_is_not_none("region", self, other)
        set_attr_if_is_not_none("country_code", self, other)
        set_attr_if_is_not_none("location_coordinates", self, other)
        set_attr_if_is_not_none("organization_name", self, other)


class BaseChecker:
    # TODO: rewrite using HttpClient
    aiohttp_connector = None

    def __init__(self, url=None, request_type="GET", timeout=None):
        if BaseChecker.aiohttp_connector is None:
            BaseChecker.aiohttp_connector = ProxyConnector(
                remote_resolve=True,
                limit=settings.NUMBER_OF_SIMULTANEOUS_REQUESTS,
                limit_per_host=settings.NUMBER_OF_SIMULTANEOUS_REQUESTS_PER_HOST,
            )
        self.request_type = request_type
        self.timeout = timeout if timeout is not None else settings.PROXY_CHECKING_TIMEOUT
        self.url = url

    @staticmethod
    def get_aiohttp_connector():
        return BaseChecker.aiohttp_connector

    @staticmethod
    def clean():
        """
        Should be called at the end of the program

        :return:
        """
        BaseChecker.aiohttp_connector.close()

    async def check(self, proxy_address: str, timeout: int = None) -> tuple:
        """
        Checks proxy and returns additional information if such was provided by checker server

        :param proxy_address: string representing proxy ("http://user@qwerty@127.0.0.1:8080")
        :param timeout: overrides timeout if not None
        :return: tuple where first item is bool indication whether proxy is working or not
        and second one is additional information structure with information like white ip address, country and so on
        """

        timeout = timeout if timeout is not None else self.timeout

        try:
            return await self._request(proxy_address, timeout)
        except (
            aiohttp.client_exceptions.ServerDisconnectedError,
            aiohttp.client_exceptions.ClientHttpProxyError,
            aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientResponseError,
            aiohttp.client_exceptions.ClientPayloadError,
            aiosocks.errors.SocksError,
            aiosocks.SocksError,
            asyncio.TimeoutError,
            ssl.CertificateError,
            aiohttp.client_exceptions.ClientOSError,
        ) as ex:
            message = str(ex).lower()

            if "too many open file" in message:
                raise OSError("Too many open files")

            if settings.DEBUG:
                # TODO: move to logs!
                print(
                    f"proxy {proxy_address} doesn't work because of exception {type(ex)}, message is {message}"
                )

        return False, None

    async def _request(self, proxy_address, timeout) -> tuple:
        checker_result = CheckerResult()

        if self.url is None:
            raise Exception()

        headers = {"User-Agent": async_requests.get_random_user_agent()}
        conn = BaseChecker.get_aiohttp_connector()

        async with aiohttp.ClientSession(
            connector=conn, connector_owner=False, request_class=ProxyClientRequest
        ) as session:
            async with session.request(
                self.request_type, self.url, proxy=proxy_address, timeout=timeout, headers=headers
            ) as response:
                is_working = await self.validate(response, checker_result)

        return is_working, checker_result

    async def validate(
        self, response: aiohttp.ClientResponse, checker_result: CheckerResult
    ) -> bool:
        """
        Implement this method. It will get response from url with http method you provided in constructor

        :param response: aiohttp response
        :param checker_result: fill this structure with information like ip address
        :return: whether proxy is working or not
        """
        raise NotImplemented()
