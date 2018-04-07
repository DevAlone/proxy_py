import json

from proxy_py import settings
from .base_app import BaseApp
from .api_v1.app import App as ApiV1App
from .frontend.app import App as FrontendApp
from aiohttp import web

import logging
import aiohttp
import aiohttp_jinja2


class ProxyProviderServer(BaseApp):
    def __init__(self, host, port, processor):
        logger = logging.getLogger("proxy_py/server")

        if settings.DEBUG:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger_file_handler = logging.FileHandler("logs/server.log")
        logger_file_handler.setLevel(logging.DEBUG)
        logger_file_handler.setFormatter(logging.Formatter(
            "%(levelname)s ~ %(asctime)s ~ %(client_ip)s ~ %(message)s"
        ))

        logger.addHandler(logger_file_handler)

        super(ProxyProviderServer, self).__init__(logger)

        self._processor = processor
        self.host = host
        self.port = port
        self._request_number = 0

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

        try:
            response = await handler(request)
            status_code = response.status
        except web.web_exceptions.HTTPException as ex:
            status_code = ex.status
            raise ex
        except BaseException as ex:
            raise ex
        finally:
            self.log_info(request, "<- data={}".format(json.dumps({
                "request_number": current_request_number,
                "status_code": status_code,
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
