import json

import async_requests
from collectors.pages_collector import PagesCollector

URL_PATTERN = (
    "https://nordvpn.com/wp-admin/admin-ajax.php?searchParameters[0][name]=proxy-country"
    "&searchParameters[0][value]=&searchParameters[1][name]=proxy-ports&searchParameters[1][value]="
    "&offset={}&limit={}&action=getProxies"
)


class Collector(PagesCollector):
    # this collector gives a lot of bad proxies
    # TODO: do something
    __collector__ = False
    processing_period = 10 * 60

    def __init__(self):
        super(Collector, self).__init__()
        self.pages_count = 10
        self.limit = 100

    async def process_page(self, page_index):
        offset = page_index * self.limit
        resp = await async_requests.get(URL_PATTERN.format(offset, self.limit))
        json_response = json.loads(resp.text)

        result = []

        for item in json_response:
            result.append("{}:{}".format(item["ip"], item["port"]))

        if result:
            self.pages_count = page_index + 2
        else:
            self.pages_count = page_index

        return result
