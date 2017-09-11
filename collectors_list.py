# TODO: refactor this shit

from collectors.collector_free_proxy_list_net import Collector as Collector1
from collectors.collector_proxy_list_org import Collector as Collector2
from collectors.collector_gatherproxy_com import Collector as Collector3
from collectors.collector_free_proxy_list_net_anonymous_proxy import Collector as Collector4
from collectors.collector_free_proxy_list_net_uk_proxy import Collector as Collector5
from collectors.collector_socks_proxy_net import Collector as Collector6
from collectors.collector_sslproxies_org import Collector as Collector7
from collectors.collector_us_proxy_org import Collector as Collector8

collectorTypes = [
    Collector1,
    Collector2,
    Collector3,
    Collector4,
    Collector5,
    Collector6,
    Collector7,
    Collector8,
]
