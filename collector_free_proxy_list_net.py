from .collector import AbstractCollector
import lxml.html
import lxml.etree

import requests


# TODO: add logging
class Collector(AbstractCollector):
    def collect(self):
        print('start collecting free-proxy-list.net')
        result = []
        try:
            html = requests.get('https://free-proxy-list.net/').text
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
        except Exception as ex:
            return []
