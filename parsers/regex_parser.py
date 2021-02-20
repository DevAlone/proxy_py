import re

# TODO: add ipv6 addresses, make domain checking better
_0_TO_255_REGEX = r"([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
DOMAIN_LETTER_REGEX = r"[a-zA-Z0-9_\-]"
PROXY_FIND_REGEX = (
    r"((?P<protocol>(http|socks4|socks5))://)?"
    r"((?P<auth_data>[a-zA-Z0-9_\.]+:[a-zA-Z0-9_\.]+)@)?"
    r"(?P<domain>"
    + r"("
    + _0_TO_255_REGEX
    + "\.){3}"
    + _0_TO_255_REGEX
    + r"|"
    + DOMAIN_LETTER_REGEX
    + r"+(\.[a-zA-Z]"
    + DOMAIN_LETTER_REGEX
    + r"+)+):"
    r"(?P<port>(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|999[0-9]|99[0-8][0-9]|9[0-8][0-9]{2}|[1-8][0-9]{3}|99[0-9]|9[0-8][0-9]|[1-8][0-9]{2}|9[0-9]|[1-8][0-9]|[1-9]))"
)
PROXY_VALIDATE_REGEX = "^" + PROXY_FIND_REGEX + "/?$"


class RegexParser:
    """
    It's used to scratch proxies from text by regular expression,
    you can pass your own expression(see docstring for parse method)
    """

    def __init__(self, expression=PROXY_FIND_REGEX, flags=0):
        """

        :param expression: expression which is used to parse proxies with named groups:
        (?P<protocol>) - for proxy protocol (socks4/5, http)
        (?P<auth_data>) - authentication data (login and password)
        (?P<domain>) - IP or domain
        (?P<port>) - port
        There is a default value which parses proxies like these ones:
        127.0.0.1:9060
        test.proxy.com:8080
        socks4://8.8.8.8:65000
        http://user:password@proxy.test.info/

        :param flags: flags that are passed to re.compile
        """

        flags |= re.MULTILINE
        self.expression = expression
        self.regex = re.compile(expression, flags)

    def parse(self, text: str) -> list:
        for match in self.regex.finditer(text):
            match = match.groupdict()
            yield match["domain"] + ":" + match["port"]
