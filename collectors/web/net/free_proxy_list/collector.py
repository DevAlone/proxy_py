import lxml.etree
import lxml.html

import async_requests
from collectors.abstract_collector import AbstractCollector


class BaseCollectorFreeProxyListNet(AbstractCollector):
    def __init__(self, url):
        super(BaseCollectorFreeProxyListNet, self).__init__()
        self.url = url

    async def collect(self):
        result = []

        res = await async_requests.get(self.url)
        html = res.text
        tree = lxml.html.fromstring(html)
        table_element = tree.xpath(".//table[@id='proxylisttable']")[0]
        rows = table_element.xpath(".//tbody/tr")
        for row in rows:
            try:
                ip = row.xpath(".//td")[0].text
                port = row.xpath(".//td")[1].text
                result.append(str(ip) + ":" + str(port))
            except:
                pass

        return result


class CollectorFreeProxyListNet(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(CollectorFreeProxyListNet, self).__init__("https://free-proxy-list.net/")


class CollectorFreeProxyListNetAnonymousProxy(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(CollectorFreeProxyListNetAnonymousProxy, self).__init__(
            "https://free-proxy-list.net/anonymous-proxy.html"
        )


class CollectorFreeProxyListNetUkProxy(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(CollectorFreeProxyListNetUkProxy, self).__init__(
            "https://free-proxy-list.net/uk-proxy.html"
        )


class CollectorSocksProxyNet(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(CollectorSocksProxyNet, self).__init__("https://socks-proxy.net/")


class CollectorSslproxiesOrg(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(CollectorSslproxiesOrg, self).__init__("https://www.sslproxies.org/")


class CollectorUsProxyOrg(BaseCollectorFreeProxyListNet):
    __collector__ = True

    def __init__(self):
        super(CollectorUsProxyOrg, self).__init__("https://www.us-proxy.org/")
