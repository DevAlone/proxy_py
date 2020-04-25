from collectors.abstract_collector import AbstractCollector

import async_requests
import json
import datetime


class Collector(AbstractCollector):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__()
        self.processing_period = 3600 * 12
        self.time_delta = datetime.timedelta(-1)

    async def collect(self):
        url = "https://checkerproxy.net/api/archive/{}".format(str(datetime.date.today() + self.time_delta))

        res = await async_requests.get(url)
        text = res.text

        json_data = json.loads(text)

        return [proxy['addr'] for proxy in json_data]


class CollectorToday(Collector):
    __collector__ = True

    def __init__(self):
        super(CollectorToday, self).__init__()
        self.processing_period = 3600 * 3
        self.time_delta = datetime.timedelta(0)
