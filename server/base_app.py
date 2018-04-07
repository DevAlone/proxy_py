import asyncio

from proxy_py import settings
from aiohttp import web

import abc
import json
import aiohttp
import aiohttp_jinja2
import jinja2
import inspect


class BaseApp:
    def __init__(self, logger=None):
        self.logger = logger
        self._app = web.Application()

        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(
            settings.TEMPLATES_PATH
        ))

    async def init(self):
        """Call it before anything else"""
        await self.setup_router()
        await self.setup_middlewares()

    @abc.abstractmethod
    async def setup_router(self):
        pass

    async def setup_middlewares(self):
        pass

    @property
    def app(self):
        return self._app

    def log_critical(self, *args, **kwargs):
        self.log('critical', *args, **kwargs)

    def log_error(self, *args, **kwargs):
        self.log('error', *args, **kwargs)

    def log_warning(self, *args, **kwargs):
        self.log('warning', *args, **kwargs)

    def log_info(self, *args, **kwargs):
        self.log('info', *args, **kwargs)

    def log_debug(self, *args, **kwargs):
        self.log('debug', *args, **kwargs)

    def log(self, level, request, message):
        if settings.DEBUG:
            client_host, client_port = request.transport.get_extra_info("peername")
            client_ip = "{}:{}".format(client_host, client_port)
        else:
            # behind nginx or other reverse proxy
            client_ip = str(request.headers.get('X-Real-IP', None))
            if client_ip is None:
                self.logger.error("Your reverse proxy doesn't present user's IP")

        getattr(self.logger, level)(message, extra={
            "client_ip": client_ip,
        })
