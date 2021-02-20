from collectors.abstract_collector import AbstractCollector
from proxy_py import settings


# TODO: save pages to collector state
class PagesCollector(AbstractCollector):
    """
    Collector for paginated APIs. Pages are started from 0.
    Here you should override ``process_page(page_index)`` method.
    This collector will care about pages, increment it on each processing
    and will reset it to 0 if there is no proxies on the page or if proxies
    are the same as those on the previous one. If you don't want such smart
    behavior, just set dynamic_pages_count to false
    and set pages_count manually.
    """

    def __init__(self):
        super(PagesCollector, self).__init__()
        self.last_proxies_list = []
        self.saved_variables.add("current_page")
        self.saved_variables.add("pages_count")
        self.saved_variables.add("last_proxies_list")

    async def collect(self):
        proxies = list(await self.process_page(self.current_page))[
            : settings.COLLECTOR_MAXIMUM_NUMBER_OF_PROXIES_PER_REQUEST
        ]

        if self.dynamic_pages_count:
            if proxies:
                self.pages_count = self.current_page + 2
                """
                for those APIs which returns
                the last page for nonexistent ones
                """
                proxies_set = set(proxies)

                if set(self.last_proxies_list) == proxies_set:
                    self.pages_count = self.current_page + 1

                self.last_proxies_list = list(proxies_set)
            else:
                self.pages_count = self.current_page + 1

        self.current_page += 1
        if self.current_page >= self.pages_count:
            self.current_page = 0

        return proxies

    async def process_page(self, page_index):
        """
        you should override this in your class derived from PagesCollector.

        `page_index` changes from 0 to pages_count(excluded)
        """
        return []

    pages_count = 0
    """set this value or use dynamic pages count"""
    current_page = 0

    dynamic_pages_count = True
    """use dynamic pages count"""

    processing_period = 60 * 10

    last_proxies_list = None
