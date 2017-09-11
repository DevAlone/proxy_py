from collectors.collector import AbstractCollector

class PagesCollector(AbstractCollector):
    def collect(self):
        # TODO: delete it later
        with open('pages_collector_debug_log', 'a') as f:
            f.write('pagesCount = {0}, currentPage = {1}, processingPeriod = {2};\n'\
                    .format(self.pagesCount, self.currentPage, self.processingPeriod))
        proxies = self.processPage(self.currentPage)
        self.currentPage += 1
        if self.currentPage >= self.pagesCount:
            self.currentPage = 0
        return proxies

    # you should realize this in your class derived from PagesCollector
    # `pageIndex` changes from 0 to pagesCount(excluded)
    def processPage(self, pageIndex):
        return []

    # and also you should set pagesCount
    pagesCount = 0
    currentPage = 0

    processingPeriod = 60 * 2