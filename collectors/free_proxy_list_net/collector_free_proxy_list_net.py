from collectors.free_proxy_list_net.base_collector_free_proxy_list_net import BaseCollectorFreeProxyListNet


class Collector(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(Collector, self).__init__('https://free-proxy-list.net/')
