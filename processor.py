import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings

import http_requests
from core.models import Proxy
import server

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
        infoLogFileHandler = logging.FileHandler('processor.log')
        infoLogFileHandler.setLevel(logging.INFO)

        self.logger.addHandler(debugFileHandler)
        self.logger.addHandler(infoLogFileHandler)

        self.logger.debug('processor initialization...')

        server.runServer(
            self,
            settings.PROXY_PROVIDER_SERVER['HOST'],
            settings.PROXY_PROVIDER_SERVER['PORT'])

    def stop(self, waitUntilFinishes=True):
        print('exiting...')
        self.isAlive = False
        server.stopServer()
        if waitUntilFinishes:
            self.join()

    def mainThreadHandler(self):
        def processCollector(collector):
            self.logger.debug('start processing collector of type "' + str(type(collector)) + '"')
            proxies = collector.collect()
            self.logger.debug('got {0} proxies from collector of type {1}'.format(len(proxies), type(collector)))
            self.processRawProxies(proxies)
            collector.lastProcessedTime = time.time()

        def processProxy(proxy):
            self.logger.debug('start processing proxy {0}'.format(proxy.toUrl()))
            checkResult = self.checkProxy(proxy)

            if checkResult:
                self.logger.debug('proxy {0} works'.format(proxy.toUrl()))
                proxy.numberOfBadChecks = 0
            else:
                proxy.numberOfBadChecks += 1

            if proxy.numberOfBadChecks > 3:
                proxy.badProxy = True
                self.logger.debug('removing proxy {0}'.format(proxy.toUrl()))

            proxy.lastCheckedTime = time.time()
            proxy.save()


        i = 0
        while self.isAlive:
            # process collectors
            for collector in self.collectors:
                if time.time() >= collector.lastProcessedTime + \
                        collector.processingPeriod:
                    self.tasks.put([processCollector, collector])

            # check proxies
            for proxy in Proxy.objects.all().filter(badProxy=False):
                # TODO: maybe add check for existent in queue
                if time.time() >= proxy.lastCheckedTime + \
                        settings.PROXY_CHECKING_PERIOD:
                    self.tasks.put([processProxy, proxy])
                    proxy.lastCheckedTime = time.time()

            time.sleep(5)

    def worker(self):
        while self.isAlive:
            item = self.tasks.get()
            if item is not None:
                # process task
                item[0](*item[1:])
            else:
                time.sleep(1)

    def addCollector(self, collector):
        self.collectors.append(collector)

    def addProxy(self, address):
        # TODO: check address
        try:
            proxy = Proxy.objects.get(address=address)
            self.logger.debug('proxy {0} already exist'.format(proxy.toUrl()))
        except Proxy.DoesNotExist:
            proxy = Proxy()
            proxy.address = address
            self.logger.debug('add proxy {0}'.format(proxy.toUrl()))
            proxy.save()

    # http://icanhazip.com/
    def checkProxy(self, proxy):
        try:
            if http_requests.get('http://icanhazip.com/', proxy, timeout=10)['code'] != 200:
                return False
        except Exception as ex:
            return False
        return True

    # TODO: add proxy with domains
    # TODO: add proxy with authorization
    def processRawProxies(self, proxies):
        def processRawProxy(proxy):
            protocols = self.detectProtocols(proxy)
            ipPort = proxy.split(':')
            if len(protocols) > 0:
                for protocol in protocols:
                    self.addProxy(protocol + "://" + ipPort[0] + ":" + ipPort[1])
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
                # protocol://domain:port
                data = proxy.split(':')
                protocol = data[0]
                # TODO: check protocol, must be http or socks or socks5
                ip = data[1][2:]
                port = data[2]
                self.addProxy(protocol + "://" + ip + ":" + port)

    def detectProtocols(self, rawProxy):
        result = []
        for i, proxies in enumerate([{
                'http': 'http://' + rawProxy,
                'https': 'https://' + rawProxy
            }, {
                'http': 'socks5h://' + rawProxy,
                'https': 'socks5h://' + rawProxy
            }]):
            # TODO: add other test sites
            try:
                res = requests.get('https://wtfismyip.com/text',
                                   timeout=5, proxies=proxies)
                if res.status_code == 200:
                    result.append("http" if i == 0 else "socks5")
            except Exception as ex:
                pass
        return result

    def join(self):
        for thread in self.threads:
            thread.join()
        self.mainThread.join()
        server.stopServer()
        if server.serverThread is not None:
            server.serverThread.join()

    threads = []
    mainThread = None
    threads_count = 0
    tasks = Queue()
    collectors = []
    logger = None
    isAlive = True
