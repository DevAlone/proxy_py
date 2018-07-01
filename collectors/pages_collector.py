from proxy_py import settings
from collectors.collector import AbstractCollector


# TODO: save pages to collector state
class PagesCollector(AbstractCollector):
    """
    Collector for paginated APIs. Pages are started from 0.
    Here you should override ``process_page(page_index)`` method.
    This collector will care about pages, increment it on each processing
    and will reset it to 0 if there is no proxies on the page or if proxies
    are the same as those on the previous one. If you don't want such smart
    behavior, just set dynamic_pages_count to false and set pages_count manually.
    """

    async def load_state(self, state):
        super(PagesCollector, self).load_state(state)
        if "_current_page" in self.data:
            self.current_page = self.data["_current_page"]

        if "_pages_count" in self.data:
            self.pages_count = self.data["_pages_count"]

    async def save_state(self, state):
        super(PagesCollector, self).save_state(state)
        self.data["_current_page"] = self.current_page
        self.data["_pages_count"] = self.pages_count

    async def collect(self):
        proxies = list(
            await self.process_page(self.current_page)
        )[:settings.COLLECTOR_MAXIMUM_NUMBER_OF_PROXIES_PER_REQUEST]

        if self.dynamic_pages_count:
            if proxies:
                self.pages_count = self.current_page + 2
                """
                for those APIs which returns
                the last page for nonexistent ones 
                """
                proxies_set = set(proxies)

                if "_last_proxies_set" in self.data:
                    if set(self.data["_last_proxies_set"]) == proxies_set:
                        self.pages_count = self.current_page + 1

                self.data["_last_proxies_set"] = list(proxies_set)
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

    """set this value or use dynamic pages count"""
    pages_count = 0
    current_page = 0
    """use dynamic pages count"""
    dynamic_pages_count = True

    processing_period = 60 * 10
