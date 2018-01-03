# TODO: add wrapper for doing requests and saving its cookies and UserAgent

class AbstractCollector:
    # this method should return proxies in any of the following formats:
    # ip:port
    # domain:port
    # protocol://ip:port
    # protocol://domain:port
    async def collect(self):
        return []

    async def load_state(self, state):
        self.last_processing_time = state.last_processing_time
        self.processing_period = state.processing_period

    async def save_state(self, state):
        state.last_processing_time = self.last_processing_time
        state.processing_period = self.processing_period

    # time in unix timestamp(seconds from 01.01.1970)
    last_processing_time = 0
    # processing period in seconds
    processing_period = 60 * 60
    # this means processing period may be changed
    # if collector returns too few proxies, it increases
    floating_processing_period = True
    # ignore settings' maximum processing period and set
    # it to value of this variable
    override_maximum_processing_period = None
    override_minimum_processing_period = None
