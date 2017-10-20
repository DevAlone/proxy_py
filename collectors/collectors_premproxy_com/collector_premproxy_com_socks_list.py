from .base_collector_premproxy_com import BaseCollectorPremProxyCom

class Collector(BaseCollectorPremProxyCom):
    def __init__(self):
        super(Collector, self).__init__('https://premproxy.com/socks-list/', 20)