from . import http_requests
from .proxy import Proxy
from . import server

from threading import Thread
import time
import requests
import re
from queue import Queue

import logging

try:
    import pydevd
except:
    pass

class Processor():
    def __init__(self, threads_count=10):
        self.threads_count = threads_count
        self.threads = []
        for i in range(self.threads_count):
            thread = Thread(target=self.worker)
            thread.start()
            self.threads.append(thread)

        self.mainThread = Thread(target=self.mainThreadHandler)
        self.mainThread.start()

        self.logger = logging.getLogger('proxy_py/processor')
        self.logger.setLevel(logging.DEBUG)
        debugFileHandler = logging.FileHandler('processor.log.debug')
        debugFileHandler.setLevel(logging.DEBUG)
        # fileHandler = logging.FileHandler('processor.log')
        # fileHandler.setLevel(logging.INFO)

        self.logger.addHandler(debugFileHandler)
        # self.logger.addHandler(fileHandler)

        self.logger.debug('processor initialization...')

        server.runServer(self)

    def mainThreadHandler(self):
        def processCollector(collector):
            self.logger.debug('start processing collector of type "' + str(type(collector)) + '"')
            proxies = collector.collect()
            self.logger.debug('got {0} proxies from collector of type {1}'.format(len(proxies), type(collector)))
            self.processRawProxies(proxies)
            collector.lastProcessedTime = time.time()

        def processProxy(proxy):
            self.logger.debug('start processing proxy {0}'.format(proxy.toUrl()))
            proxy.lastCheckResult = self.checkProxy(proxy)

            if proxy.lastCheckResult:
                self.logger.debug('proxy {0} works'.format(proxy.toUrl()))
                proxy.numberOfBadChecks = 0
            else:
                proxy.numberOfBadChecks += 1

            if proxy.numberOfBadChecks > 3:
                try:
                    self.proxies.remove(proxy)
                    self.logger.debug('removing proxy {0}'.format(proxy.toUrl()))
                except:
                    pass
            proxy.lastCheckedTime = time.time()

        i = 0
        while True:
            for collector in self.collectors:
                if time.time() >= collector.lastProcessedTime + \
                        collector.processingPeriod:
                    self.tasks.put([processCollector, collector])

            # check proxies
            # TODO: make several checks

            for proxy in self.proxies:
                # print(proxy.toUrl())
                if time.time() >= proxy.lastCheckedTime + \
                        proxy.checkingPeriod and proxy:
                    self.tasks.put([processProxy, proxy])
                    proxy.lastCheckedTime = time.time()

            time.sleep(5)

    def worker(self):
        while True:
            item = self.tasks.get()
            if item is not None:
                # process task
                item[0](*item[1:])
            else:
                time.sleep(1)

    def addCollector(self, collector):
        # if type(collector) != Collector:
        #     raise Exception('type of collector shoud be "Collector"')
        self.collectors.append(collector)

    def addProxy(self, proxy):
        if type(proxy) != Proxy:
            raise Exception('type of proxy shoud be "Proxy"')
        self.proxies.add(proxy)
        self.logger.debug('add proxy {0}'.format(proxy.toUrl()))

    # http://icanhazip.com/
    def checkProxy(self, proxy):
        try:
            if http_requests.get('http://icanhazip.com/', proxy)['code'] != 200:
                return False
        except Exception as ex:
            return False
        return True

    # TODO: add proxy with domains
    def processRawProxies(self, proxies):
        def processRawProxy(proxy):
            protocols = self.detectProtocols(proxy)
            ipPort = proxy.split(':')
            if len(protocols) > 0:
                self.addProxy(Proxy(protocols, ipPort[0], ipPort[1]))
            else:
                self.logger.debug('unable to determine protocol of raw proxy {0}'.format(proxy))

        for proxy in proxies:
            proxy = proxy.lower()
            self.logger.debug('start processing raw proxy {0}'.format(proxy))
            if re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}$', proxy):
                # just ip address with port
                self.tasks.put([processRawProxy, proxy])
            elif re.match(
                    r'^[a-z0-9]+://([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}$',
                    proxy):
                data = proxy.split(':')
                protocol = data[0]
                # TODO: check protocol, must be http or socks or socks5
                ip = data[1][2:]
                port = data[2]
                self.addProxy(Proxy([protocol], ip, port))

    def detectProtocols(self, rawProxy):
        result = []
        for i in range(2):
            # TODO: add other test sites
            try:
                if i == 0:
                    res = requests.get('https://wtfismyip.com/text', timeout=5,
                                    proxies={'http': 'http://' + rawProxy,
                                             'https': 'https://' + rawProxy})
                elif i == 1:
                    res = requests.get('https://wtfismyip.com/text', timeout=5,
                                   proxies={'http': 'socks5h://' + rawProxy,
                                            'https': 'socks5h://' + rawProxy})
                if res.status_code == 200:
                    result.append("http" if i == 0 else "socks5")
            except Exception as ex:
                pass
        return result

    def join(self):
        for thread in self.threads:
            thread.join()
        self.mainThread.join()

    threads = []
    mainThread = None
    threads_count = 0
    tasks = Queue()
    collectors = []
    proxies = set()
    logger = None
