import abc

import aiohttp_jinja2
import jinja2
from aiohttp import web

import settings


class BaseApp:
    def __init__(self, logger=None):
        self.logger = logger
        self._app = web.Application()

        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(
            settings.server.templates_path
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

    def log_exception(self, *args, **kwargs):
        self.log('exception', *args, **kwargs)

    def log_warning(self, *args, **kwargs):
        self.log('warning', *args, **kwargs)

    def log_info(self, *args, **kwargs):
        self.log('info', *args, **kwargs)

    def log_debug(self, *args, **kwargs):
        self.log('debug', *args, **kwargs)

    def log(self, level, request, message):
        # behind nginx or other reverse proxy
        client_ip = str(request.headers.get("X-Real-IP", "None"))

        if client_ip == "None" or client_ip.startswith("127.0.0.1"):
            self.logger.error("Your reverse proxy doesn't present user's IP", extra={"client_ip": client_ip})

        getattr(self.logger, level)(message, extra={
            "client_ip": client_ip,
        })
