# TODO: add wrapper for doing requests and saving its cookies and UserAgent
from proxy_py import settings

import json
import models


class AbstractCollector:
    """Base class for all types of collectors"""

    async def collect(self):
        """
        this method should return proxies in any of the following formats:

        ::

            ip:port
            domain:port
            protocol://ip:port
            protocol://domain:port

        """

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

    last_processing_time = 0
    """time in unix timestamp(seconds from 01.01.1970)"""

    processing_period = 60 * 60
    """processing period in seconds"""

    # TODO: create this feature
    floating_processing_period = True
    """
    this means processing period may be changed
    if collector returns too few proxies, it will be increased
    """

    override_maximum_processing_period = None
    """
    ignore settings' maximum processing period and set
    it to value of this variable
    """

    override_minimum_processing_period = None

    data = {}
    """
    here you can store some information,
    it will be written into and read from database
    by magic, don't worry about it :)
    Just don't use names starting with underscore
    like this one: _last_page
    """
