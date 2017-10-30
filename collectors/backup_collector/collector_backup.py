from collectors.collector import AbstractCollector

import json


class Collector(AbstractCollector):
    async def collect(self):

        with open('collectors/backup_collector/proxies') as f:
            data = json.loads(f.read())['data']

        return [proxy['address'] for proxy in data]
