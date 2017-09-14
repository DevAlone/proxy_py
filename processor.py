import os
import django


from core.models import Proxy
import proxy_utils

from django.conf import settings

from threading import Thread
import time
import re
from queue import Queue
import logging

try:
    import pydevd
except:
    pass


# main class which collects proxies from collectors
# checks them and saves in database
class Processor():
    def __init__(self, threads_count=10):
        self.threads_count = threads_count
        self.threads = []
        for i in range(self.threads_count):
            thread = Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

        self.mainThread = Thread(target=self.mainThreadHandler)
        self.daemon = True
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


    def stop(self, waitUntilFinishes=True):
        print('exiting...')
        self.isAlive = False
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
            checkResult = proxy_utils.checkProxy(proxy)

            if checkResult:
                self.logger.debug('proxy {0} works'.format(proxy.toUrl()))
                proxy.numberOfBadChecks = 0
                proxy.badProxy = False
            else:
                proxy.numberOfBadChecks += 1

            if proxy.numberOfBadChecks > 5:
                proxy.badProxy = True
                self.logger.debug('removing proxy {0}'.format(proxy.toUrl()))

            proxy.lastCheckedTime = time.time()
            proxy.save()

        while self.isAlive:
            # process collectors
            for collector in list(self.collectors.values()):
                if time.time() >= collector.lastProcessedTime + \
                        collector.processingPeriod:
                    self.tasks.put([processCollector, collector])

            # check proxies
            for proxy in Proxy.objects.all():
                 if time.time() >= proxy.lastCheckedTime + \
                        (settings.BAD_PROXY_CHECKING_PERIOD if proxy.badProxy else settings.PROXY_CHECKING_PERIOD):
                    self.tasks.put([processProxy, proxy])
                    proxy.lastCheckedTime = time.time()

            # TODO: make it better
            while self.tasks.qsize() > 0:
                time.sleep(1)
                if not self.isAlive:
                    break
            # self.tasks.join()
            # time.sleep(0.5)


    def worker(self):
        while self.isAlive:
            item = None
            try:
                item = self.tasks.get(timeout=2)
            except:
                pass
            if item is not None:
                # process task
                try:
                    item[0](*item[1:])
                except Exception as ex:
                    self.logger.error("Exception in worker: " + str(ex))
                    print("Exception in worker(see logs for details)")
                except:
                    self.logger.error("Exception in worker")
                    print("Exception in worker")
                finally:
                    self.tasks.task_done()
            else:
                time.sleep(1)


    def addCollectorOfType(self, collectorType):
        if collectorType not in self.collectors:
            self.collectors[collectorType] = collectorType()


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


    # TODO: add proxy with domains
    # TODO: add proxy with authorization
    def processRawProxies(self, proxies):
        def processRawProxy(proxy):
            protocols = proxy_utils.detectRawProxyProtocols(proxy)
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

    def join(self):
        for thread in self.threads:
            thread.join()
        self.mainThread.join()


    threads = []
    mainThread = None
    threads_count = 0
    tasks = Queue()
    collectors = {}
    logger = None
    isAlive = True
