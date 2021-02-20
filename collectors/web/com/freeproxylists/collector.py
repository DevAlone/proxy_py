import asyncio
import re

from bs4 import BeautifulSoup

import http_client
from collectors import AbstractCollector

SLEEP_BETWEEN_PAGES_SECONDS = 1


class Collector(AbstractCollector):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__()
        # it provides really a lot of proxies so we'll check it rarely
        # 24 hours
        self.processing_period = 24 * 3600
        self.url = "http://freeproxylists.com"

    async def collect(self):
        html = await http_client.get_text(self.url)
        soup = BeautifulSoup(html, features="lxml")

        for link in soup.select("a"):
            link = link["href"].strip()

            if re.match(r"^/[a-zA-Z0-9_-]+\.html$", link):
                async for proxy in self.collect_from_page(link):
                    yield proxy

    async def collect_from_page(self, page_link):
        html = await http_client.get_text(self.url + page_link)

        soup = BeautifulSoup(html, features="lxml")

        for link in soup.select("a"):
            link = link["href"].strip()

            regex = r"^([a-zA-Z0-9_-]+)/([0-9]+)\.html$"
            match = re.match(regex, link)

            if match:
                type_of_proxies, proxies_id = match.groups()
                url = f"{self.url}/load_{type_of_proxies}_{proxies_id}.html"

                async for proxy in self.collect_from_table(url):
                    yield proxy

    async def collect_from_table(self, table_url):
        html = await http_client.get_text(table_url)

        soup = BeautifulSoup(html, features="lxml")

        table_text = soup.find("quote").contents[0]
        soup = BeautifulSoup(table_text, features="lxml")

        for tr in soup.find_all("tr"):
            children = tr.find_all("td")
            if len(children) != 2:
                continue

            ip, port = [child.contents[0] for child in children]
            proxy = f"{ip}:{port}"
            yield proxy

        await asyncio.sleep(SLEEP_BETWEEN_PAGES_SECONDS)
