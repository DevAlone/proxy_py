from collectors.pages_collector import PagesCollector

import requests
import lxml.html
import lxml.etree
import re
import base64

class Collector(PagesCollector):
    def __init__(self):
        self.pagesCount = 57

    def processPage(self, pageIndex):
        result = []
        formData = {
            'Type': 'elite',
            'PageIdx': pageIndex + 1,
            'Uptime': 0
        }
        html = requests.post('http://www.gatherproxy.com/proxylist/anonymity/?t=Elite', data=formData).text
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

