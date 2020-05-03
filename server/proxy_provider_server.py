import asyncio
import sys
import json
import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web

import settings
import storage
from .base_app import BaseApp
from .api_v1.app import App as ApiV1App
from .api_v2.app import App as ApiV2App
from .frontend.app import App as FrontendApp


class ProxyProviderServer(BaseApp):
    def __init__(self, host, port):
        logger = logging.getLogger("proxy_py/server")
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        # TODO: rewrite to use the default logger
        logger_handler = logging.StreamHandler(sys.stdout)
        logger_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        logger_handler.setFormatter(logging.Formatter(settings.log_format))

        logger.addHandler(logger_handler)

        super(ProxyProviderServer, self).__init__(logger)

        self.host = host
        self.port = port
        self._request_number = 0

    def start(self):
        loop = asyncio.get_event_loop()

        # TODO: use the storage
        postgres_storage = storage.PostgresStorage()
        loop.run_until_complete(postgres_storage.init())

        loop.run_until_complete(self.init())

        return web.run_app(self._app, host=self.host, port=self.port, loop=loop)

    async def setup_router(self):
        api_v1_app = ApiV1App(logger=self.logger)
        await api_v1_app.init()
        api_v2_app = ApiV2App(logger=self.logger)
        await api_v2_app.init()
        frontend_app = FrontendApp(logger=self.logger)
        await frontend_app.init()

        self._app.add_subapp('/api/v1/', api_v1_app.app)
        self._app.add_subapp('/api/v2/', api_v2_app.app)
        self._app.add_subapp('/i/', frontend_app.app)

    async def setup_middlewares(self):
        error_middleware = self.error_pages_handler({
            404: self.handle_404,
            500: self.handle_500,
        })

        self.app.middlewares.append(error_middleware)
        self.app.middlewares.append(self.logging_middleware)

    @web.middleware
    async def logging_middleware(self, request: aiohttp.ClientRequest, handler):
        self._request_number += 1

        current_request_number = self._request_number

        request_data = {
            "request_number": current_request_number,
            "method": request.method,
            "url": str(request.url),
            "user-agent": request.headers.get("User-Agent", None),
        }

        if request.body_exists:
            request_data["body"] = (await request.read()).decode()

        self.log_info(request, "-> data={}".format(json.dumps(request_data)))

        status_code = None
        exc = None

        try:
            response = await handler(request)
            status_code = response.status
        except web.web_exceptions.HTTPException as ex:
            status_code = ex.status
            exc = ex
            raise ex
        except BaseException as ex:
            exc = ex
            raise ex
        finally:
            self.log_info(request, "<- data={}".format(json.dumps({
                "request_number": current_request_number,
                "status_code": status_code,
                "exception": str(exc),
            })))

        return response

    def error_pages_handler(self, overrides):
        @web.middleware
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
