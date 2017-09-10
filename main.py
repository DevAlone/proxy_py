#!/usr/bin/env python3


import requests
from processor import Processor
from collectors.collector_free_proxy_list_net import Collector as Collector1
from collectors.collector_awmproxy_net import Collector as Collector2
from core.models import Proxy

import time
import signal

proxies = []

class ProgrammKiller:
    kill = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.setKillFlag)
        signal.signal(signal.SIGTERM, self.setKillFlag)

    def setKillFlag(self, signum, frame):
        self.kill = True


if __name__ == "__main__":
    killer = ProgrammKiller()

    proxyProcessor = Processor(25)
    proxyProcessor.addCollector(Collector1())
    # proxyProcessor.addCollector(Collector2())

    while True:
        print('main thread: proxies count is' +
              str(Proxy.objects.count()))
        # for proxy in proxyProcessor.proxies:
        #     print('main thread: ' + proxy.toUrl())
        if killer.kill:
            proxyProcessor.stop()
            break
        time.sleep(1)

    proxyProcessor.join()
