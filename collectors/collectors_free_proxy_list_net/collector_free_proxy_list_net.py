from .base_collector_free_proxy_list_net import BaseCollectorFreeProxyListNet

class Collector(BaseCollectorFreeProxyListNet):
    def __init__(self):
        super(Collector, self).__init__('https://free-proxy-list.net/')