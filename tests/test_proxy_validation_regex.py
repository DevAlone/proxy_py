from processor import PROXY_VALIDATE_REGEX
import re


valid_proxies = [
    '192.168.0.1:8080',
    '8.8.8.8:1',
    '99.99.99.99:65535',
    'socks4://99.99.99.99:666',
    'socks5://99.99.99.99:66/',
    'http://99.99.99.99:66',
    'user999_1:asdfAADSF_@8.8.4.4:8080',
    'http://user999_1:asdfAADSF_@8.8.4.4:8080',
    'socks4://user999_1:asdfAADSF_@8.8.4.4:8080',
    'socks5://user999_1:asdfAADSF_@8.8.4.4:8080',
    'http://user999_1:asdfAADSF_@proxy.google.com:8080',
    'http://user999_1:asdfAADSF_@proxy.google:8080',
    'http://user999_1:asdfAADSF_@localhost:8080',
    'the-best-proxy-ever.com:80'
]

invalid_proxies = [
    '256.54.11.0:8080',
    '255.255.255.1:0',
    '246.119.80.80:65536',
    '246.119.80.80:100000',
    '246.119.80.80/100000',
    'socks://99.99.99.99:66',
    '80.66.161.99',
]


def is_proxy_valid(proxy: str):
    return bool(re.match(PROXY_VALIDATE_REGEX, proxy))


def test_valid_proxies():
    for proxy in valid_proxies:
        assert is_proxy_valid(proxy)


def test_invalid_proxies():
    for proxy in invalid_proxies:
        assert not is_proxy_valid(proxy)
