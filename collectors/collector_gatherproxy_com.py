from collectors.pages_collector import PagesCollector

import async_requests
import lxml.html
import lxml.etree
import re
import base64

class Collector(PagesCollector):
    def __init__(self):
        self.pages_count = 57

    async def processPage(self, page_index):
        result = []
        formData = {
            'Type': 'elite',
            'PageIdx': page_index + 1,
            'Uptime': 0
        }
        res = await async_requests.post('http://www.gatherproxy.com/proxylist/anonymity/?t=Elite', data=formData)
        html = res.text
        tree = lxml.html.fromstring(html)
        tableElement = \
            tree.xpath(".//table[@id='tblproxy']")[0]
        tableText = lxml.etree.tostring(tableElement).decode()
        matches = re.findall(r"document\.write\('([0-9\.]+)'\).+?document\.write\(gp\.dep\('(.+?)'\)\)", tableText, re.DOTALL)
        for m in matches:
            ip = m[0]
            cryptedPort = m[1]
            port = int(cryptedPort, 16)
            proxy = "{0}:{1}".format(ip, port)
            result.append(proxy)

        return result

