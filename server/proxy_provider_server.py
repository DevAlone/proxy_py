from proxy_py import settings
from .base_app import BaseApp
from .api_v1.app import App as ApiV1App
from .frontend.app import App as FrontendApp
from aiohttp import web

import logging
import aiohttp
import jinja2
import aiohttp_jinja2


# TODO: refactor it
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


class ProxyProviderServer(BaseApp):
    def __init__(self, host, port, processor):

        super(ProxyProviderServer, self).__init__(_logger)

        self._processor = processor
        self.host = host
        self.port = port

    async def start(self, loop):
        await self.init()

        server = await loop.create_server(
            self._app.make_handler(),
            self.host,
            self.port
        )

        return server

    async def setup_router(self):
        api_v1_app = ApiV1App(logger=self.logger)
        await api_v1_app.init()
        frontend_app = FrontendApp(logger=self.logger)
        await frontend_app.init()

        self._app.add_subapp('/api/v1/', api_v1_app.app)
        self._app.add_subapp('/i/', frontend_app.app)

    async def setup_middlewares(self):
        error_middleware = self.error_pages_handler({
            404: self.handle_404,
            500: self.handle_500,
        })

        self._app.middlewares.append(error_middleware)

    def error_pages_handler(self, overrides):
        @aiohttp.web.middleware
        async def middleware(request, handler):
            try:
                response = await handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return response
                else:
                    return await override(request, response)
            except aiohttp.web.HTTPException as ex:
                override = overrides.get(ex.status)
                if override is None:
                    raise
                else:
                    return await override(request, ex)

        return middleware

    async def handle_404(self, request, _):
        resp = aiohttp_jinja2.render_template(
            "index.html", request, {}
        )

        resp.set_status(404)

        return resp

    async def handle_500(self, *_):
        return aiohttp.web.Response(status=500, text="Server error")
