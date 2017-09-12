from collectors.pages_collector import PagesCollector

import requests
import lxml.html
import lxml.etree
import re
import base64

class Collector(PagesCollector):
    def __init__(self):
        self.pagesCount = 20

    def processPage(self, pageIndex):
        result = []
        url  = 'https://premproxy.com/list/'
        if pageIndex > 0:
            url += '{0}.htm'.format(pageIndex + 1)

        html = requests.get(url=url).text
        tree = lxml.html.fromstring(html)
        elements = \
            tree.xpath(".//td[starts-with(@data-label, 'IP:port')]")
        for el in elements:
            proxy = el.text.strip()
            result.append(proxy)

        return result
