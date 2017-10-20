# TODO: refactor this shit
from .collectors_free_proxy_list_net import list as collectors_free_proxy_list_net_list
from .collectors_premproxy_com import list as collectors_premproxy_com_list

from .collector_gatherproxy_com import Collector as Collector1
from .collector_proxy_list_org import Collector as Collector2

collectors = [
    Collector1,
    Collector2
]

collectors.extend(collectors_free_proxy_list_net_list.collectors)
collectors.extend(collectors_premproxy_com_list.collectors)
