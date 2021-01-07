import http_client
from collectors import AbstractCollector
from parsers import RegexParser


class Collector(AbstractCollector):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__()
        # 30 minutes
        self.processing_period = 30 * 60
        """
        floating period means proxy_py will be changing 
        period to not make extra requests and handle 
        new proxies in time, you don't need to change 
        it in most cases
        """
        # self.floating_processing_period = False

    async def collect(self):
        url = "http://www.89ip.cn/tqdl.html?num=9999&address=&kill_address=&port=&kill_port=&isp="
        # send a request to get html code of the page
        html = await http_client.get_text(url)
        # and just parse it using regex parser with a default rule to parse
        # proxies like this:
        # 8.8.8.8:8080
        return RegexParser().parse(html)
