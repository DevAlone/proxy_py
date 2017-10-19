from django.db import models
import re

PROXY_VALIDATE_REGEX = \
r'^(?P<protocol>[a-z0-9]+)://((?P<login>[a-zA-Z0-9_\.]+):(?P<password>[a-zA-Z0-9_\.]+)@)?(?P<domain>([a-z0-9_]+\.)+[a-z0-9_]+):(?P<port>[0-9]{1,5})/?$'

class Proxy(models.Model):
    # TODO: add address validation
    # http://user:password@proxy.asdf.asdf.ru:8080/
    address = models.CharField(max_length=255, primary_key=True)
    whiteIp = models.GenericIPAddressField(null=True)
    # TODO: maybe change to unsigned type
    lastCheckedTime = models.BigIntegerField(default=0)
    numberOfBadChecks = models.IntegerField(default=0)
    badProxy = models.BooleanField(default=False)
    uptime = models.BigIntegerField(default=0)


    def toUrl(self, protocol=None):
        # TODO: cache it
        matches = re.match(PROXY_VALIDATE_REGEX, self.address)
        if matches is not None:
            if protocol is None:
                res = matches.group('protocol')
            else:
                res = protocol

            res += '://'
            if      matches.group('login') is not None and \
                    matches.group('password') is not None:
                res += matches.group('login') + ':'
                res += matches.group('password') + '@'
            res += matches.group('domain') + ':'
            res += matches.group('port')
            return res
        return self.address


    def getProtocol(self):
        matches = re.match(PROXY_VALIDATE_REGEX, self.address)
        return matches.group('protocol')


    def toRawProxy(self):
        matches = re.match(PROXY_VALIDATE_REGEX, self.address)
        res = ""
        if matches.group('login') is not None and matches.group('password') is not None:
            res += matches.group('login') + ':' + matches.group('password') + '@'
        res += matches.group('domain') + ':' + matches.group('port')
        return res


    def fromString(proxyStr):
        proxy = Proxy()
        proxy.address = proxyStr
        return proxy


    class Meta:
        indexes = [
            models.Index(fields=['whiteIp']),
            models.Index(fields=['badProxy']),
        ]

    def __str__(self):
        return self.address

    __repr__ = __str__
