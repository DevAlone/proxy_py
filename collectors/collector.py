# TODO: add wrapper for doing requests and saving its cookies and UserAgent
from proxy_py import settings

import json
import models


class AbstractCollector:
    """
    this method should return proxies in any of the following formats:
    ip:port
    domain:port
    protocol://ip:port
    protocol://domain:port
    """
    async def collect(self):
        return []

    async def _collect(self):
        """do not use!"""
        return (await self.collect())[:settings.COLLECTOR_MAXIMUM_NUMBER_OF_PROXIES_PER_REQUEST]

    async def load_state(self, state: models.CollectorState):
        self.last_processing_time = state.last_processing_time
        self.processing_period = state.processing_period
        self.data = json.loads(state.data) if state.data is not None and state.data else {}

    async def set_state(self, state: models.CollectorState):
        state.last_processing_time = self.last_processing_time
        state.processing_period = self.processing_period
        state.data = json.dumps(self.data)

    """time in unix timestamp(seconds from 01.01.1970)"""
    last_processing_time = 0
    """processing period in seconds"""
    processing_period = 60 * 60
    """
    this means processing period may be changed
    if collector returns too few proxies, it will be increased
    """
    # TODO: create this feature
    floating_processing_period = True
    """
    ignore settings' maximum processing period and set
    it to value of this variable
    """
    override_maximum_processing_period = None
    override_minimum_processing_period = None
    """
    here you can store some information,
    it will be written into and read from database
    by magic, don't worry about it :)
    Just don't use names starting with underscore
    like this one: _last_page
    """
    data = {}
