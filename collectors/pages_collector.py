from collectors.collector import AbstractCollector


class PagesCollector(AbstractCollector):
    async def collect(self):
        proxies = await self.process_page(self.current_page)
        self.current_page += 1
        if self.current_page >= self.pages_count:
            self.current_page = 0
        return proxies

    async def process_page(self, page_index):
        """
        you should override this in your class derived from PagesCollector
        `pageIndex` changes from 0 to pagesCount(excluded)
        """
        return []

    # and also you should set pages_count
    pages_count = 0
    current_page = 0

    processing_period = 60 * 10
