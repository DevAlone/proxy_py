#!/usr/bin/env python3

import requests
from processor import Processor
from core.models import Proxy

import time
import signal
import os

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

    dirPath = os.path.dirname(os.path.realpath(__file__))

    while True:
        try:
            fromScriptVariables = {}
            exec(open(os.path.join(dirPath, 'collectors_list.py')).read(), fromScriptVariables)
            for CollectorType in fromScriptVariables['collectorTypes']:
                proxyProcessor.addCollectorOfType(CollectorType)
        except:
            print('some shit happened with file collectors_list.py')
        try:
            print('main thread: proxies count is' +
              str(Proxy.objects.count()))
        except:
            print('some shit happened')

        if killer.kill:
            proxyProcessor.stop()
            break
        time.sleep(10)

    proxyProcessor.join()
