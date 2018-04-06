import asyncio

from proxy_py import settings
from aiohttp import web

import abc
import json
import aiohttp
import aiohttp_jinja2
import jinja2


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
