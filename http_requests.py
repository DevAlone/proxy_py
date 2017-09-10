import requests


def get(url, proxy=None, timeout=10):
    proxies = {}

    if proxy is not None:
        if proxy.getProtocol() == "http":
            proxies = {
                'http': proxy.toUrl('http'),
                'https': proxy.toUrl('https'),
            }
        elif proxy.getProtocol() == "socks" or proxy.getProtocol() == "socks5":
            proxies = {
                'http': proxy.toUrl('socks5h'),
                'https': proxy.toUrl('socks5h'),
            }
        else:
            proxies = {
                'http': proxy.toUrl(),
                'https': proxy.toUrl(),
            }

    result = requests.get(url, proxies=proxies, timeout=timeout)

    return {
        'code': result.status_code,
        'content': result.text
    }
