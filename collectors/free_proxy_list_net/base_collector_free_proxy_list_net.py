from collectors.collector import AbstractCollector
import lxml.html
import lxml.etree

import async_requests


class BaseCollectorFreeProxyListNet(AbstractCollector):
    def __init__(self, url):
        self.url = url

    async def collect(self):
        result = []

        res = await async_requests.get(self.url)
        html = res.text
        tree = lxml.html.fromstring(html)
        table_element = \
            tree.xpath(".//table[@id='proxylisttable']")[0]
        rows = table_element.xpath('.//tbody/tr')
        for row in rows:
            try:
                ip = row.xpath('.//td')[0].text
                port = row.xpath('.//td')[1].text
                result.append(str(ip) + ':' + str(port))
            except:
                pass

        return result
