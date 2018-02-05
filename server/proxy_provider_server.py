import json
import time

import datetime

import functools
from proxy_py import settings
from server.api_request_handler import ApiRequestHandler
from models import session, Proxy, ProxyCountItem, CollectorState

import aiohttp
import aiohttp.web
import logging
import aiohttp_jinja2
import jinja2


_proxy_provider_server = None
_logger = logging.getLogger('proxy_py/server')
_logger.setLevel(logging.DEBUG)
debug_file_handler = logging.FileHandler('logs/server.debug.log')
debug_file_handler.setLevel(logging.DEBUG)
error_file_handler = logging.FileHandler('logs/server.error.log')
error_file_handler.setLevel(logging.ERROR)
error_file_handler = logging.FileHandler('logs/server.warning.log')
error_file_handler.setLevel(logging.WARNING)
info_file_handler = logging.FileHandler('logs/server.log')
info_file_handler.setLevel(logging.INFO)

_logger.addHandler(debug_file_handler)
_logger.addHandler(error_file_handler)
_logger.addHandler(info_file_handler)

_api_request_handler = ApiRequestHandler(_logger)


def get_response_wrapper(template_name):
    def decorator_wrapper(func):
        @functools.wraps(func)
        @aiohttp_jinja2.template(template_name)
        async def wrap(self, *args, **kwargs):
            good_proxies_count = session.query(Proxy).filter(Proxy.number_of_bad_checks == 0).count()

            bad_proxies_count = session.query(Proxy).filter(Proxy.number_of_bad_checks > 0)\
                .filter(Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD).count()

            dead_proxies_count = session.query(Proxy)\
                .filter(Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD).count()

            response = {
                "bad_proxies_count": bad_proxies_count,
                "good_proxies_count": good_proxies_count,
                "dead_proxies_count": dead_proxies_count,
            }
            response.update(await func(self, *args, **kwargs))
            return response
        return wrap

    return decorator_wrapper


class ProxyProviderServer:
    @staticmethod
    def get_proxy_provider_server(host, port, processor):
        global _proxy_provider_server
        if _proxy_provider_server is None:
            _proxy_provider_server = ProxyProviderServer(host, port, processor)
        return _proxy_provider_server

    def __init__(self, host, port, processor):
        self._processor = processor
        self.host = host
        self.port = port

    async def start(self, loop):
        app = aiohttp.web.Application()
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("server/templates"))
        app.router.add_post('/', self.post)
        app.router.add_get('/', self.index)
        app.router.add_get('/get/proxy/', self.get_proxies_html)
        app.router.add_get('/get/proxy_count_item/', self.get_proxy_count_items_html)
        app.router.add_get('/get/collector_state/', self.get_collector_state_html)
        app.router.add_get('/get/best/http/proxy/', self.get_best_http_proxy)

        server = await loop.create_server(app.make_handler(), self.host, self.port)
        return server

    async def get_best_http_proxy(self, request):
        proxy_address = session.query(Proxy).filter(Proxy.number_of_bad_checks == 0)\
            .filter(Proxy.raw_protocol == Proxy.PROTOCOLS.index("http"))\
            .order_by("response_time").first().address

        return aiohttp.web.Response(text=proxy_address)

    async def post(self, request):
        client_address = request.transport.get_extra_info('peername')
        host, port = (None, None)

        if client_address is not None:
            host, port = client_address
        else:
            client_address = (host, port)

        data = await request.read()

        with open("logs/server_connections", 'a') as f:
            f.write("client - {}:{}, data - {}\n".format(host, port, data))

        try:
            data = json.loads(data.decode())

            response = _api_request_handler.handle(client_address, data)
        except ValueError:
            response = {
                'status': 'error',
                'status_code': 400,
                'error_message': "Your request doesn't look like request",
            }

        if 'status_code' in response:
            status_code = response['status_code']
        else:
            if response['status'] != 'ok':
                status_code = 500
            else:
                status_code = 200

            response['status_code'] = status_code

        return aiohttp.web.json_response(response, status=status_code)

    @get_response_wrapper("collector_state.html")
    async def get_collector_state_html(self, request):
        return {
            "collector_states": list(session.query(CollectorState).all())
        }

    @get_response_wrapper("proxies.html")
    async def get_proxies_html(self, request):
        proxies = list(session.query(Proxy)
                       .filter(Proxy.number_of_bad_checks == 0)
                       .order_by(Proxy.response_time))

        current_timestamp = time.time()

        return {
            "proxies": [{
                "address": proxy.address,
                "response_time": proxy.response_time / 1000 if proxy.response_time is not None else None,
                "uptime": datetime.timedelta(
                    seconds=int(current_timestamp - proxy.uptime)) if proxy.uptime is not None else None,
                "bad_uptime": datetime.timedelta(
                    seconds=int(current_timestamp - proxy.bad_uptime)) if proxy.bad_uptime is not None else None,
                "last_check_time": proxy.last_check_time,
                "checking_period": proxy.checking_period,
                "number_of_bad_checks": proxy.number_of_bad_checks,
                "bad_proxy": proxy.bad_proxy,
                "white_ipv4": proxy.white_ipv4,
                "city": proxy.city,
                "region": proxy.region,
                "country_code": proxy.country_code,
            } for proxy in proxies]
        }

    @get_response_wrapper("proxy_count_items.html")
    async def get_proxy_count_items_html(self, request):
        return {
            "proxy_count_items": list(session.query(ProxyCountItem).order_by(ProxyCountItem.timestamp))
        }

    @aiohttp_jinja2.template("index.html")
    async def index(self, request):
        return {}
