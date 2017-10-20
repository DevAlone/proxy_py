from collectors.collector import AbstractCollector
import lxml.html
import lxml.etree

import async_requests


# TODO: add logging
class BaseCollectorFreeProxyListNet(AbstractCollector):
    def __init__(self, url):
        self.url = url

    async def collect(self):
        result = []

        res = await async_requests.get(self.url)
        html = res.text
        tree = lxml.html.fromstring(html)
        tableElement = \
            tree.xpath(".//table[@id='proxylisttable']")[0]
        rows = tableElement.xpath('.//tbody/tr')
        for row in rows:
            try:
                ip = row.xpath('.//td')[0].text
                port = row.xpath('.//td')[1].text
                result.append(str(ip) + ':' + str(port))
            except Exception as ex:
                pass

        return result