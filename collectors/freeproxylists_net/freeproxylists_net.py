from collectors.pages_collector import PagesCollector

import async_requests
import re
import lxml
import lxml.html
from urllib import parse


BASE_URL = "http://freeproxylists.net/?page={}"


class Collector(PagesCollector):
    __collector__ = True
    # pages from 1

    def __init__(self):
        self.dynamic_pages_count = True

    async def process_page(self, page_index):
        # TODO: fix it
        result = []
        # data = {
        #     "recaptcha_challenge_field": "03AMPJSYUZslP6_QOT6YguO3_jhhi2HJd81u0WHPe6eWrbMIStFeXQkfFV16GGQQuHZ_Za5HKMPKYTpPfLu-K5I8G8EAzbM8OTihtneSzgolnQB47SAhg5xw5sEHaTQj_B1I8u3gnw-Ts9ng3T6UAgi4jKTteAzoqQ4_DyND2DqWOX2kAVjCJKhLEYVZdp6z3-Qi14CS2PXRegNRALrYkBeALq5S3tY51y0A",
        #     "recaptcha_response_field": "RPETS+ATTENTION",
        # }
        # resp = await async_requests.post(BASE_URL.format(page_index + 1), data)

        headers = {
            "Cookie": "hl=en; pv=14; userno=20180103-012864; from=direct; visited=2018%2F01%2F03+19%3A35%3A50; __utmb=251962462.16.10.1514975753; __utmc=251962462; __utmt=1; __atuvc=15%7C1; __atuvs=5a4cb2077864569600e; __utma=251962462.2036678170.1513732296.1513732296.1514975753.2; __utmz=251962462.1513732296.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=251962462.Ukraine"
        }

        resp = await async_requests.get(BASE_URL.format(page_index + 1), headers=headers)
        text = resp.text
        # with open("/home/user/python_projects/proxy_py/collectors/freeproxylists_net/fake_data") as f:
        #     text = f.read()
        try:
            tree = lxml.html.fromstring(text)
            table_element = tree.xpath(".//table[@class='DataGrid']")[0]
        except BaseException:
            raise Exception("table not found: {}".format(text))

        rows = table_element.xpath('.//tr')
        for row in rows:
            try:
                ip = row.xpath('.//td/script')[0].text
                port = row.xpath('.//td')[1].text
                if ip is None or port is None:
                    continue

                ip = parse.unquote(ip)
                ip = re.search(r">([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*?</a>", ip)
                if ip is None:
                    continue
                ip = ip.groups()[0]

                result.append("{}:{}".format(ip, port))
            except IndexError:
                pass

        return result
