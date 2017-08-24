import requests


def get(url, proxy=None, timeout=10):
    proxies = {}
    if proxy is not None:
        if "http" in proxy.protocols or "https" in proxy.protocols:
            proxies = {
                'http': proxy.toUrl('http'),
                'https': proxy.toUrl('https'),
            }
        elif "socks" in proxy.protocols or "socks5" in proxy.protocols:
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
