

class AbstractCollector:
    # this method should return proxies in any of following formats:
    # ip:port
    # domain:port
    # protocol://ip:port
    # protocol://domain:port
    def collect(self):
        return []

    # time in unix timestamp(seconds from 01.01.1970)
    lastProcessedTime = 0
    # processing period in seconds
    processingPeriod = 60 * 10
