import time

import datetime

from server.api_request_handler import ApiRequestHandler
from models import session, Proxy

import aiohttp
import aiohttp.web
import logging


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
        app.router.add_get('/get/proxy/', self.get_proxies_html)

        server = await loop.create_server(app.make_handler(), self.host, self.port)
        return server

    async def post(self, request):
        client_address = request.transport.get_extra_info('peername')

        try:
            data = await request.json()
            response = _api_request_handler.handle(client_address, data)
        except:
            raise
            response = {
                'status': "error",
                'error': "Your request doesn't look like request",
            }

        return aiohttp.web.json_response(response)

    async def get_proxies_html(self, request):
        try:
            html="""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Go away!</title>"""
            html += """
            <style>
            #proxy_table {
                width: 100%;
            }
            #proxy_table td {
                padding: 10px;
            }
            </style>
            """
            html += "</head><body>"

            html += """<table id="proxy_table">"""
            html += "<thead>"
            html += "<tr>"

            html += "<td>address</td>"
            html += "<td>response_time</td>"
            html += "<td>uptime</td>"
            html += "<td>last_check_time</td>"
            html += "<td>number_of_bad_checks</td>"
            html += "<td>bad_proxy</td>"

            html += "</tr>"
            html += "</thead>"

            html += "<tbody>"

            current_timestamp = int(time.time())
            i = 0
            for proxy in session.query(Proxy).filter(Proxy.response_time != None).order_by(Proxy.response_time):
                html += "<tr>"
                html += "<td>{}</td>".format(proxy.address)
                html += "<td>{}ms</td>".format(proxy.response_time / 1000 if proxy.response_time is not None else None)
                html += """<td id="proxy_{}_uptime">{}</td>""".format(i,
                                                    datetime.timedelta(seconds=int(current_timestamp - proxy.uptime)))
                html += "<td>{}</td>".format(proxy.last_check_time)
                html += "<td>{}</td>".format(proxy.number_of_bad_checks)
                html += "<td>{}</td>".format(proxy.bad_proxy)
                html += "</tr>"
                # html += """
                # <script>
                # proxy_{}_uptime.textContent = new Date({});
                # </script>
                # """.format(i, proxy.uptime * 1000)
                i += 1

            html += "<tbody>"

            html += "</table>"

            html += "</body></html>"
        except Exception as ex:
            _logger.exception(ex)

        return aiohttp.web.Response(headers={'Content-Type': 'text/html'}, body=html)

    async def get(self, request):
        return aiohttp.web.Response(headers={'Content-Type': 'text/html'}, body="""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Go away!</title>
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

<iframe width="100%" height="100%" src="https://www.youtube.com/embed/7OBx-YwPl8g?rel=0&autoplay=1" frameborder="0" 
allowfullscreen></iframe>
</body>

</html>
""")
