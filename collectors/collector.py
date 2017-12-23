class AbstractCollector:
    # this method should return proxies in any of the following formats:
    # ip:port
    # domain:port
    # protocol://ip:port
    # protocol://domain:port
    async def collect(self):
        return []

    # time in unix timestamp(seconds from 01.01.1970)
    last_processing_time = 0
    # processing period in seconds
    processing_period = 60 * 30
