from collectors.premproxy_com.base_collector_premproxy_com import BaseCollectorPremProxyCom


class Collector(BaseCollectorPremProxyCom):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__('https://premproxy.com/list/', 20)
