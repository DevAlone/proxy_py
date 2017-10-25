from core.models import Proxy
from server.api_request_handler import ApiRequestHandler

import asyncio
import aiohttp
import aiohttp.web

import threading
import logging
import re

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
        app.router.add_post('/', self.post)
        app.router.add_get('/', self.get)

        server = await loop.create_server(app.make_handler(), self.host, self.port)
        return server

    async def post(self, request):
        client_address = request.transport.get_extra_info('peername')

        data = await request.json()

        return aiohttp.web.json_response(_api_request_handler.handle(client_address, data))

    async def get(self, request):
        return aiohttp.web.Response(text="""HTTP/1.1 200 OK
Server: Apache/1.3.37
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>title</title>
<style>
html, body {
    width: 100%;
    height: 100%;
    background: #eee;
    padding: 0;
    margin: 0;
    line-height: 0;
}
</style>
</head>
<body>

<iframe width="100%" height="100%" src="https://www.youtube.com/embed/7OBx-YwPl8g?rel=0&autoplay=1" frameborder="0" allowfullscreen></iframe>
</body>

</html>
""")



# class RequestHandler(asyncore.dispatcher_with_send):
#     MAX_REQUEST_SIZE = 1024  # 1 KB
#     TCP_REQUEST_THRESHOLD = 10
#
#     def handle_read(self):
#         try:
#             client_address = self.socket.getpeername()
#
#             data = self.recv(self.MAX_REQUEST_SIZE)
#             if data:
#                 if len(data) < self.TCP_REQUEST_THRESHOLD:
#                     for urlData in self.getUrls():
#                         self.send(urlData)
#                 else:
#                     method, url, headers, post_data = parse_http(data.decode('utf-8'))
#                     if method is not None:
#                         self.send(_api_request_handler.handle(client_address, method, headers, post_data))
#                     else:
#                         self.send(b"It's not a request\n")
#         except:
#             _logger.exception("Error in RequestHandler")
#         finally:
#             self.close()
#
#     def getUrls(self):
#         try:
#             for proxy in Proxy.objects.all().filter(badProxy=False).order_by('uptime'):
#                 yield "{}\n".format(proxy.toUrl()).encode('utf-8')
#         except:
#             _logger.exception("Error in RequestHandler.getUrls(self)")