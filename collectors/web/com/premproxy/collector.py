from collectors.pages_collector import PagesCollector
from lxml import etree
from py_mini_racer import py_mini_racer

import lxml.html
import re
import async_requests


class BaseCollectorPremProxyCom(PagesCollector):
    def __init__(self, url, pages_count):
        super(BaseCollectorPremProxyCom, self).__init__()
        self.url = url
        self.pages_count = pages_count

    async def process_page(self, page_index):
        result = []
        if page_index > 0:
            self.url += '%02d.htm' % (page_index + 1, )

        resp = await async_requests.get(url=self.url)
        html = resp.text
        tree = lxml.html.fromstring(html)
        elements = tree.xpath(".//td[starts-with(@data-label, 'IP:port')]")

        code_table_url = re.findall(r'script src="(/js(-socks)?/.+?\.js)', html)[0][0]

        code_table = (
            await async_requests.get('https://premproxy.com' + code_table_url)
        ).text.replace('eval', '')
        ports_code_table = {
            match[0]: match[1]
            for match in re.findall(
                r"\$\('.([a-z0-9]+)'\)\.html\(([0-9]+)\)",
                py_mini_racer.MiniRacer().execute(code_table),
            )
        }
        for el in elements:
            element_html = str(etree.tostring(el))
            address, port = re.search(
                r'(?P<address>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\|(?P<port>[a-z0-9]+)',
                element_html
            ).groups()
            try:
                port = ports_code_table[port]
            except KeyError as ex:
                raise Exception('symbol is not present in code table: {}. address: {}'.format(str(ex), address))
            proxy = '{}:{}'.format(address, port)
            result.append(proxy)

        return result


class Collector(BaseCollectorPremProxyCom):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__('https://premproxy.com/list/', 20)


class CollectorSocksList(BaseCollectorPremProxyCom):
    __collector__ = True

    def __init__(self):
        super(CollectorSocksList, self).__init__('https://premproxy.com/socks-list/', 20)
