from .collector_free_proxy_list_net import Collector as Collector1
from .collector_free_proxy_list_net_anonymous_proxy import Collector as Collector2
from .collector_free_proxy_list_net_uk_proxy import Collector as Collector3
from .collector_socks_proxy_net import Collector as Collector4
from .collector_sslproxies_org import Collector as Collector5
from .collector_us_proxy_org import Collector as Collector6

collectors = [
    Collector1,
    Collector2,
    Collector3,
    Collector4,
    Collector5,
    Collector6
]