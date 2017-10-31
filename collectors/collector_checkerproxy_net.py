from collectors.collector import AbstractCollector

import async_requests
import json
import datetime


class Collector(AbstractCollector):
    def __init__(self):
        self.processing_period = 3600 * 12

    async def collect(self):
        url = "https://checkerproxy.net/api/archive/{}".format(str(datetime.date.today()))

        res = await async_requests.get(url)
        text = res.text

        json_data = json.loads(text)

        return [proxy['addr'] for proxy in json_data]
