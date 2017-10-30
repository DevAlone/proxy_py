from collectors.collector import AbstractCollector

class PagesCollector(AbstractCollector):
    async def collect(self):
        # TODO: delete it later
        with open('pages_collector_debug_log', 'a') as f:
            f.write('pagesCount = {0}, currentPage = {1}, processingPeriod = {2};\n' \
                    .format(self.pages_count, self.current_page, self.processing_period))
        proxies = await self.processPage(self.current_page)
        self.current_page += 1
        if self.current_page >= self.pages_count:
            self.current_page = 0
        return proxies

    # you should realize this in your class derived from PagesCollector
    # `pageIndex` changes from 0 to pagesCount(excluded)
    async def processPage(self, page_index):
        return []

    # and also you should set pagesCount
    pages_count = 0
    current_page = 0

    processing_period = 60 * 10
