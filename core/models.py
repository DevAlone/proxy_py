from django.db import models
import re

PROXY_VALIDATE_REGEX = \
r'^(?P<protocol>[a-z0-9]+)://((?P<login>[a-zA-Z0-9_\.]+):(?P<password>[a-zA-Z0-9_\.]+)@)?(?P<domain>([a-z0-9_]+\.)+[a-z0-9_]+):(?P<port>[0-9]{1,5})/?$'

class Proxy(models.Model):
    PROTOCOLS = (
        'http',
        'socks4',
        'socks5',
    )

    _protocol = models.IntegerField()
    auth_data = models.CharField(max_length=64, null=True)
    domain = models.CharField(max_length=128)
    port = models.PositiveIntegerField()

    white_ip_v4 = models.BinaryField(max_length=4, null=True)
    white_ip_v6 = models.BinaryField(max_length=16, null=True)

    # TODO: maybe change to unsigned type
    last_check_time = models.BigIntegerField(default=0)
    number_of_bad_checks = models.IntegerField(default=0)
    bad_proxy = models.BooleanField(default=False)
    uptime = models.BigIntegerField(default=0)


    @property
    def address(self):
        return self.to_url()


    @property
    def protocol(self):
        return self.PROTOCOLS[self._protocol]


    def to_url(self, protocol=None):
        address = protocol if protocol is not None else self.PROTOCOLS[self._protocol]
        address += "://"
        if self.auth_data:
            address += self.auth_data + "@"

        address += "{}:{}".format(self.domain, self.port)

        return address


    def get_protocol(self):
        return self.PROTOCOLS[self._protocol]


    class Meta:
        indexes = [
            models.Index(fields=['_protocol']),
            models.Index(fields=['auth_data']),
            models.Index(fields=['port']),
            models.Index(fields=['white_ip_v4']),
            models.Index(fields=['white_ip_v6']),
            models.Index(fields=['last_check_time']),
            models.Index(fields=['number_of_bad_checks']),
            models.Index(fields=['bad_proxy']),
            models.Index(fields=['uptime']),
        ]

        unique_together = (
            ("_protocol", "auth_data", "domain", "port")
        )


    def __str__(self):
        return self.to_url()

    __repr__ = __str__