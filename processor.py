from core.models import Proxy
import proxy_utils

from django.conf import settings


import asyncio
import time
import re
import logging
from queue import Queue

try:
    import pydevd
except:
    pass


# main class which collects proxies from collectors
# checks them and saves in database
class Processor():
    def __init__(self):
        self.logger = logging.getLogger('proxy_py/processor')
        self.logger.setLevel(logging.DEBUG)
        debugFileHandler = logging.FileHandler('processor.log.debug')
        debugFileHandler.setLevel(logging.DEBUG)
        infoLogFileHandler = logging.FileHandler('processor.log')
        infoLogFileHandler.setLevel(logging.INFO)

        self.logger.addHandler(debugFileHandler)
        self.logger.addHandler(infoLogFileHandler)

        self.logger.debug('processor initialization...')

    def exec(self, killer):
        loop = asyncio.get_event_loop()
        while not killer.kill:
            tasks = []
            for collector in list(self.collectors.values()):
                if time.time() >= collector.lastProcessedTime + collector.processingPeriod:
                    tasks.append(asyncio.ensure_future(self._processCollector(collector)))

            #     try:
            #         await task
            #     except Exception as ex:
            #         self.logger.exception("Error in collector")
            #     except:
            #         self.logger.exception("Error in collector")

            # check proxies
            for proxy in Proxy.objects.all():
                if time.time() >= proxy.lastCheckedTime + \
                        (settings.BAD_PROXY_CHECKING_PERIOD if proxy.badProxy else settings.PROXY_CHECKING_PERIOD):
                    tasks.append(asyncio.ensure_future(self._processProxy(proxy)))
                    if len(tasks) > 500:
                        break

            loop.run_until_complete(asyncio.wait(tasks))
            tasks.clear()

    async def _processCollector(self, collector):
        # TODO: make it async
        self.logger.debug('start processing collector of type "' + str(type(collector)) + '"')
        proxies = await collector.collect()
        self.logger.debug('got {0} proxies from collector of type {1}'.format(len(proxies), type(collector)))
        await self.processRawProxies(proxies)
        collector.lastProcessedTime = time.time()

    async def _processProxy(self, proxy):
        self.logger.debug('start processing proxy {0}'.format(proxy.toUrl()))
        checkResult = await proxy_utils.checkProxy(proxy)

        if checkResult:
            self.logger.debug('proxy {0} works'.format(proxy.toUrl()))
            proxy.numberOfBadChecks = 0
            if proxy.badProxy:
                proxy.uptime = time.time()
            proxy.badProxy = False
        else:
            proxy.numberOfBadChecks += 1

        if proxy.numberOfBadChecks > 5:
            proxy.badProxy = True
            self.logger.debug('removing proxy {0}'.format(proxy.toUrl()))

        proxy.lastCheckedTime = time.time()
        proxy.save()


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
            proxy.uptime = time.time()
            self.logger.debug('add proxy {0}'.format(proxy.toUrl()))
            proxy.save()


    # TODO: add proxy with domains
    # TODO: add proxy with authorization
    async def processRawProxies(self, proxies):
        for proxy in proxies:
            proxy = proxy.lower()
            self.logger.debug('start processing raw proxy {0}'.format(proxy))
            if re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}$', proxy):
                # just ip address with port
                await self.processRawProxy(proxy)
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

    async def processRawProxy(self, proxy):
        protocols = await proxy_utils.detectRawProxyProtocols(proxy)
        ipPort = proxy.split(':')
        if len(protocols) > 0:
            for protocol in protocols:
                self.addProxy(protocol + "://" + ipPort[0] + ":" + ipPort[1])
        else:
            self.logger.debug('unable to determine protocol of raw proxy {0}'.format(proxy))

    collectors = {}
    logger = None
