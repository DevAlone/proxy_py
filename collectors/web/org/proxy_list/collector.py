import base64
import re

import lxml.etree
import lxml.html

import async_requests
from collectors.pages_collector import PagesCollector


class Collector(PagesCollector):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__()
        self.pages_count = 10

    async def process_page(self, page_index):
        result = []
        res = await async_requests.get(
            "http://proxy-list.org/english/index.php?p={0}".format(page_index + 1)
        )
        html = res.text
        tree = lxml.html.fromstring(html)
        proxy_elements = tree.xpath(
            ".//div[@id='proxy-table']//div[@class='table']//li[@class='proxy']"
        )
        for element in proxy_elements:
            # noinspection PyUnresolvedReferences
            element_data = lxml.etree.tostring(element)
            base64_proxy = re.search(r"Proxy\('(.+?)'\)", element_data.decode()).group(
                1
            )
            proxy = base64.b64decode(base64_proxy).decode()
            result.append(proxy)
        return result
