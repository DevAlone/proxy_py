import re

from lxml import etree, html

import async_requests
from collectors.pages_collector import PagesCollector


class Collector(PagesCollector):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__()
        # TODO: remove?
        self.pages_count = 57

    async def process_page(self, page_index):
        result = []
        form_data = {"Type": "elite", "PageIdx": page_index + 1, "Uptime": 0}
        url = "http://www.gatherproxy.com/proxylist/anonymity/?t=Elite"
        res = await async_requests.post(url, data=form_data)
        html_res = res.text
        tree = html.fromstring(html_res)
        table_element = tree.xpath(".//table[@id='tblproxy']")[0]
        table_text = etree.tostring(table_element).decode()
        matches = re.findall(
            r"document\.write\('([0-9.]+)'\).+?document\.write\(gp\.dep\('(.+?)'\)\)",
            table_text,
            re.DOTALL,
        )

        for m in matches:
            ip = m[0]
            crypted_port = m[1]
            port = int(crypted_port, 16)
            proxy = "{0}:{1}".format(ip, port)
            result.append(proxy)

        return result
