from collectors.abstract_collector import AbstractCollector
from parsers.regex_parser import RegexParser

import http_client


class Collector(AbstractCollector):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__()
        self.processing_period = 30 * 60  # 30 minutes
        '''
        floating period means proxy_py will be changing 
        period to not make extra requests and handle 
        new proxies in time, you don't need to change 
        it in most cases
        '''
        # self.floating_processing_period = False

    async def collect(self):
        url = 'http://www.89ip.cn/tqdl.html?num=9999&address=&kill_address=&port=&kill_port=&isp='
        return []
        # html = await http_client.get_text(url)
        with open('/tmp/mock') as f:
            html = f.read()

        return RegexParser().parse(html)
