from parsers.regex_parser import PROXY_VALIDATE_REGEX

import re


class ValidationError(Exception):
    pass


def retrieve(proxy) -> tuple:
    protocol = auth_data = domain = port = None

    if type(proxy) is str:
        matches = re.match(PROXY_VALIDATE_REGEX, proxy)
        if matches:
            matches = matches.groupdict()
            auth_data = matches["auth_data"]
            domain = matches["domain"]
            port = matches["port"]
        else:
            raise ValidationError("Proxy doesn't match regex")
    elif type(proxy) is dict:
        auth_data = proxy["auth_data"] if "auth_data" in proxy else None
        domain = proxy["domain"] if "domain" in proxy else None
        port = proxy["port"] if "port" in proxy else None
        str_proxy = ''
        if auth_data is not None and auth_data:
            str_proxy += auth_data + '@'

        str_proxy += domain + ':' + port
        return retrieve(str_proxy)
    else:
        raise ValidationError(
            "Bad type. Type is \"{}\"".format(type(proxy), proxy)
        )

    if protocol is not None:
        if protocol not in ('socks', 'socks4', 'socks5', 'http'):
            raise ValidationError("Bad protocol")

    if auth_data is None:
        auth_data = ''

    if type(domain) is not str:
        raise ValidationError("Bad proxy(domain isn't string)")

    if type(port) is not str:
        raise ValidationError("Bad proxy(port isn't string)")


    return protocol, auth_data, domain, port
