import proxy_validator

valid_proxies = [
    "192.168.0.1:8080",
    "8.8.8.8:1",
    "99.99.99.99:65535",
    "socks4://99.99.99.99:666",
    "socks5://99.99.99.99:66/",
    "http://99.99.99.99:66",
    "user999_1:asdfAADSF_@8.8.4.4:8080",
    "http://user999_1:asdfAADSF_@8.8.4.4:8080",
    "socks4://user999_1:asdfAADSF_@8.8.4.4:8080",
    "socks5://user999_1:asdfAADSF_@8.8.4.4:8080",
    "http://user999_1:asdfAADSF_@proxy.google.com:8080",
    "http://user999_1:asdfAADSF_@proxy.google:8080",
    "the-best-proxy-ever.com:80",
]

invalid_proxies = [
    "256.54.11.0:8080",
    "255.255.255.1:0",
    "246.119.80.80:65536",
    "246.119.80.80:100000",
    "246.119.80.80/100000",
    "socks://99.99.99.99:66",
    "80.66.161.99",
    "padding-top:1",
    "margin:80",
    # don't consider localhost as valid
    "http://user999_1:asdfAADSF_@localhost:8080",
]


def check_proxy(proxy: str, should_be_valid=True):
    try:
        proxy_validator.retrieve(proxy)
        if not should_be_valid:
            raise AssertionError("Proxy shouldn't be considered as valid")
    except proxy_validator.ValidationError as ex:
        if should_be_valid:
            raise AssertionError(
                "Proxy should be considered as valid. Message: {}".format(ex)
            )


def test_valid_proxies():
    for proxy in valid_proxies:
        check_proxy(proxy, True)


def test_invalid_proxies():
    for proxy in invalid_proxies:
        check_proxy(proxy, False)
