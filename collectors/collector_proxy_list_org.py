from collectors.pages_collector import PagesCollector

import async_requests
import lxml.html
import lxml.etree
import re
import base64

class Collector(PagesCollector):
    def __init__(self):
        self.pages_count = 10

    async def processPage(self, page_index):
        result = []
        res = await async_requests.get('http://proxy-list.org/english/index.php?p={0}'.format(page_index + 1))
        html = res.text
        tree = lxml.html.fromstring(html)
        proxyElements = \
            tree.xpath(".//div[@id='proxy-table']//div[@class='table']//li[@class='proxy']")
        for element in proxyElements:
            elementData = lxml.etree.tostring(element)
            base64Proxy = re.search(r"Proxy\('(.+?)'\)", elementData.decode()).group(1)
            proxy = base64.b64decode(base64Proxy).decode()
            result.append(proxy)
        return result
