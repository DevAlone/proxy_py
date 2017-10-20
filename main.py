#!/usr/bin/env python3

# TODO: fix socks proxies

import init_django
import settings
from processor import Processor
import proxy_provider_server
from program_killer import ProgrammKiller
import collectors_list

proxies = []

killer = ProgrammKiller()

if __name__ == "__main__":
    killer = ProgrammKiller()

    proxyProcessor = Processor()
    for CollectorType in collectors_list.collectorTypes:
        proxyProcessor.addCollectorOfType(CollectorType)

    proxy_provider_server.runServer(
        proxyProcessor,
        settings.PROXY_PROVIDER_SERVER['HOST'],
        settings.PROXY_PROVIDER_SERVER['PORT'])

    try:
        proxyProcessor.exec(killer)
    except Exception as ex:
        print("Some shit happened: {}".format(ex))


    proxy_provider_server.stopServer()