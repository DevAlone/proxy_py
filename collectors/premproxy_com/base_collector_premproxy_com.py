from collectors.pages_collector import PagesCollector
import async_requests

import lxml.html
import lxml.etree


class BaseCollectorPremProxyCom(PagesCollector):
    def __init__(self, url, pages_count):
        self.url = url
        self.pages_count = pages_count

    async def process_page(self, page_index):
        result = []
        if page_index > 0:
            self.url += '{0}.htm'.format(page_index + 1)

        resp = await async_requests.get(url=self.url)
        html = resp.text
        tree = lxml.html.fromstring(html)
        elements = \
            tree.xpath(".//td[starts-with(@data-label, 'IP:port')]")
        for el in elements:
            proxy = el.text.strip()
            result.append(proxy)

        return result
