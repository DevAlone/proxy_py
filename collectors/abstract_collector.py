# TODO: add wrapper for doing requests and saving its cookies and UserAgent
from proxy_py import settings

import json
import models


# TODO: refactor saving state
class AbstractCollector:
    """Base class for all types of collectors"""

    __collector__ = False
    """Set this variable to True in your collector's implementation"""

    def __init__(self):
        self.data = {}
        self.saved_variables = set()

    async def collect(self):
        """
        This method should return proxies in any of the following formats:

        ::

            ip:port
            domain:port
            protocol://ip:port
            protocol://domain:port


        ip can be both ipv4 and ipv6

        will support yield in the future, now just return list
        """

        return []

    async def _collect(self):
        """Do not use! It is called on collector's processing automatically"""

        # TODO: uncomment when python 3.6 come to ubuntu lts
        # i = 0
        # async for proxy in self.collect():
        #     if i > settings.COLLECTOR_MAXIMUM_NUMBER_OF_PROXIES_PER_REQUEST:
        #         break

        #     yield proxy
        #     i += 1
        proxies = list(await self.collect())
        proxies = proxies[:settings.COLLECTOR_MAXIMUM_NUMBER_OF_PROXIES_PER_REQUEST]
        self.last_processing_proxies_count = len(proxies)
        return proxies

    async def load_state(self, state: models.CollectorState):
        """
        Function for loading collector's state from database model.
        It's called automatically, don't worry. All you can do is
        to override without forgetting to call parent's method like this:

        ::

            async def load_state(self, state):
                super(MyCollector, self).load_state(state)
                # do something here
        """
        self.last_processing_time = state.last_processing_time
        self.processing_period = state.processing_period
        self.last_processing_proxies_count = state.last_processing_proxies_count
        self.data = json.loads(state.data) if state.data is not None and state.data else {}
        if '_variables' in self.data:
            for var_name in self.data['_variables']:
                setattr(self, var_name, self.data['_variables'][var_name])

    async def save_state(self, state: models.CollectorState):
        """
        Function for saving collector's state to database model.
        It's called automatically, don't worry.
        """
        state.last_processing_time = self.last_processing_time
        state.processing_period = self.processing_period
        state.last_processing_proxies_count = self.last_processing_proxies_count

        if self.saved_variables is not None:
            for var_name in self.saved_variables:
                if '_variables' not in self.data:
                    self.data['_variables'] = {}

                self.data['_variables'][var_name] = getattr(self, var_name)

        state.data = json.dumps(self.data)

    last_processing_time = 0
    """time in unix timestamp(seconds from 01.01.1970)"""

    last_processing_proxies_count = 0
    """how many proxies we got on last request, do not change manually"""

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
    it to the value of this variable
    """

    override_minimum_processing_period = None
    """
    ignore settings' minimum processing period and set
    it to the value of this variable, for example
    when some collector has requests time limit
    """

    data = None
    """
    here you can store some information,
    it will be written into and read from database
    by magic, don't worry about it :)
    If you're curious, see process_collector_of_state() function
    from processor.py file

    Don't use names starting with the underscore
    like this one: _last_page
    """

    saved_variables = None
    """
    Set of variables which are saved to database automatically(inside data dict)
    """

