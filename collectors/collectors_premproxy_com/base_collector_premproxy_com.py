from collectors.pages_collector import PagesCollector

import requests
import lxml.html
import lxml.etree

class BaseCollectorPremProxyCom(PagesCollector):
    def __init__(self, url, pagesCount):
        self.url = url
        self.pagesCount = pagesCount

    async def processPage(self, pageIndex):
        result = []
        if pageIndex > 0:
            self.url += '{0}.htm'.format(pageIndex + 1)

        html = requests.get(url=self.url).text
        tree = lxml.html.fromstring(html)
        elements = \
            tree.xpath(".//td[starts-with(@data-label, 'IP:port')]")
        for el in elements:
            proxy = el.text.strip()
            result.append(proxy)

        return result
