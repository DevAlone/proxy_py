from proxy_py import settings
import peewee
import peewee_async

db = peewee_async.PooledPostgresqlDatabase(
    *settings.DATABASE_CONNECTION_ARGS,
    **settings.DATABASE_CONNECTION_KWARGS,
)


class Proxy(peewee.Model):
    class Meta:
        database = db
        db_table = 'proxies'
        indexes = (
            (('raw_protocol', 'auth_data', 'domain', 'port'), True),
            (('auth_data', 'domain', 'port'), False),  # important!
            (('raw_protocol',), False),
            (('auth_data',), False),
            (('domain',), False),
            (('port',), False),
            (('number_of_bad_checks',), False),
            (('last_check_time',), False),
            (('checking_period',), False),
            (('uptime',), False),
            (('bad_uptime',), False),
            (('response_time',), False),
            (('_white_ipv4',), False),
            (('_white_ipv6',), False),
            (('country_code',), False),
        )

    PROTOCOLS = (
        'http',
        'socks4',
        'socks5',
    )

    raw_protocol = peewee.SmallIntegerField(null=False)
    domain = peewee.CharField(settings.DB_MAX_DOMAIN_LENGTH, null=False)
    port = peewee.IntegerField(null=False)
    auth_data = peewee.CharField(settings.DB_AUTH_DATA_MAX_LENGTH, default='', null=False)

    checking_period = peewee.IntegerField(default=settings.MIN_PROXY_CHECKING_PERIOD, null=False)
    last_check_time = peewee.IntegerField(default=0, null=False)
    number_of_bad_checks = peewee.IntegerField(default=0, null=False)
    uptime = peewee.IntegerField(default=None, null=True)
    bad_uptime = peewee.IntegerField(default=None, null=True)
    # in microseconds
    response_time = peewee.IntegerField(default=None, null=True)
    # TODO: consider storing as binary
    _white_ipv4 = peewee.CharField(16, null=True)
    _white_ipv6 = peewee.CharField(45, null=True)
    city = peewee.TextField(null=True)
    region = peewee.TextField(null=True)
    country_code = peewee.CharField(3, null=True)

    def get_raw_protocol(self):
        return self.raw_protocol

    @property
    def address(self):
        return self.to_url()

    @property
    def protocol(self):
        return self.PROTOCOLS[int(self.raw_protocol)]

    @protocol.setter
    def protocol(self, protocol):
        self.raw_protocol = self.PROTOCOLS.index(protocol)

    @property
    def bad_proxy(self):
        return self.number_of_bad_checks > 0

    @property
    def white_ipv4(self):
        return self._white_ipv4

    @white_ipv4.setter
    def white_ipv4(self, value):
        self._white_ipv4 = value

    @property
    def white_ipv6(self):
        return self._white_ipv6

    @white_ipv6.setter
    def white_ipv6(self, value):
        self._white_ipv6 = value

    def to_url(self, protocol=None):
        address = protocol if protocol is not None else self.PROTOCOLS[int(self.raw_protocol)]
        address += "://"
        if self.auth_data:
            address += self.auth_data + "@"

        address += "{}:{}".format(self.domain, self.port)

        return address

    def __str__(self):
        return self.to_url()

    __repr__ = __str__


class ProxyCountItem(peewee.Model):
    class Meta:
        database = db
        db_table = 'proxy_count_items'

    timestamp = peewee.IntegerField(primary_key=True)
    good_proxies_count = peewee.IntegerField(null=False)
    bad_proxies_count = peewee.IntegerField(null=False)
    dead_proxies_count = peewee.IntegerField(null=False)


class CollectorState(peewee.Model):
    class Meta:
        database = db
        db_table = 'collector_states'
        indexes = (
            (('processing_period',), False),
            (('last_processing_time',), False),
        )

    # python module name
    identifier = peewee.TextField(unique=True)
    processing_period = peewee.IntegerField(null=False)
    last_processing_time = peewee.IntegerField(null=False)
    last_processing_proxies_count = peewee.IntegerField(default=0, null=False)
    last_processing_new_proxies_count = peewee.IntegerField(default=0, null=False)
    data = peewee.TextField(default=None, null=True)


class StatBaseModel(peewee.Model):
    class Meta:
        database = db

    timestamp = peewee.BigIntegerField(primary_key=True)


class NumberOfProxiesToProcess(StatBaseModel):
    class Meta:
        db_table = 'number_of_proxies_to_process'

    good_proxies = peewee.IntegerField(null=False)
    bad_proxies = peewee.IntegerField(null=False)
    dead_proxies = peewee.IntegerField(null=False)


_silent = True
Proxy.create_table(_silent)
ProxyCountItem.create_table(_silent)
CollectorState.create_table(_silent)
NumberOfProxiesToProcess.create_table(_silent)

db = peewee_async.Manager(db)
