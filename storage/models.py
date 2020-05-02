import peewee
import peewee_async

import proxy_py_types

raw_db = peewee_async.PooledPostgresqlDatabase(None)


class Proxy(peewee.Model):
    class Meta:
        database = raw_db
        db_table = "proxies"
        indexes = (
            (("raw_protocol", "auth_data", "domain", "port"), True),
            (("auth_data", "domain", "port"), False),  # important!
            (("raw_protocol",), False),
            (("auth_data",), False),
            (("domain",), False),
            (("port",), False),
            (("number_of_bad_checks",), False),
            (("next_check_time",), False),
            (("last_check_time",), False),
            (("checking_period",), False),
            (("uptime",), False),
            (("bad_uptime",), False),
            (("response_time",), False),
            (("_white_ipv4",), False),
            (("_white_ipv6",), False),
        )

    raw_protocol = peewee.SmallIntegerField(null=False)
    domain = peewee.TextField(null=False)
    port = peewee.IntegerField(null=False)
    auth_data = peewee.TextField(default="", null=False)

    checking_period = peewee.IntegerField(default=0, null=False)
    last_check_time = peewee.IntegerField(default=0, null=False)
    next_check_time = peewee.IntegerField(default=0, null=False)
    number_of_bad_checks = peewee.IntegerField(default=0, null=False)
    uptime = peewee.IntegerField(default=None, null=True)
    bad_uptime = peewee.IntegerField(default=None, null=True)
    # in microseconds
    response_time = peewee.IntegerField(default=None, null=True)
    # TODO: consider storing as binary
    _white_ipv4 = peewee.CharField(16, null=True)
    _white_ipv6 = peewee.CharField(45, null=True)

    def get_raw_protocol(self):
        return self.raw_protocol

    @property
    def location(self):
        return None
        # TODO: implement location
        # if location_database_reader is None:
        #     return None
        #
        # # TODO: handle the situation when it wasn't found
        # response = location_database_reader.city(self.domain)
        #
        # return {
        #     "latitude": response.location.latitude,
        #     "longitude": response.location.longitude,
        #     "country_code": response.country.iso_code,
        #     "country": response.country.name,
        #     "city": response.city.name,
        # }

    @property
    def address(self) -> str:
        return self.to_url()

    @property
    def protocol(self) -> proxy_py_types.Protocol:
        return proxy_py_types.Protocol(self.raw_protocol)

    @protocol.setter
    def protocol(self, protocol: proxy_py_types.Protocol):
        self.raw_protocol = protocol.value

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

    @property
    def login(self) -> str:
        if ":" not in self.auth_data:
            return ""

        return str(self.auth_data).split(":")[0]

    @property
    def password(self) -> str:
        if ":" not in self.auth_data:
            return ""

        return str(self.auth_data).split(":")[1]

    def to_url(self) -> str:
        login = ""
        password = ""
        if self.auth_data:
            login, password = str(self.auth_data).split(":")

        return proxy_py_types.proxy_to_url(
            proxy_py_types.Protocol(int(self.raw_protocol)),
            login,
            password,
            self.address,
            self.port,
        )

    def __str__(self) -> str:
        return self.to_url()

    __repr__ = __str__


class ProxyCountItem(peewee.Model):
    class Meta:
        database = raw_db
        db_table = "proxy_count_items"

    timestamp = peewee.IntegerField(primary_key=True)
    good_proxies_count = peewee.IntegerField(null=False)
    bad_proxies_count = peewee.IntegerField(null=False)
    dead_proxies_count = peewee.IntegerField(null=False)


class CollectorState(peewee.Model):
    class Meta:
        database = raw_db
        db_table = "collector_states"
        indexes = (
            (("processing_period",), False),
            (("last_processing_time",), False),
        )

    # python module name
    identifier = peewee.TextField(unique=True)
    processing_period = peewee.IntegerField(null=False)
    last_processing_time = peewee.IntegerField(null=False)
    last_processing_proxies_count = peewee.IntegerField(default=0, null=False)
    # TODO: add new proxies
    last_processing_new_proxies_count = peewee.IntegerField(default=0, null=False)
    data = peewee.TextField(default=None, null=True)


class StatBaseModel(peewee.Model):
    class Meta:
        database = raw_db

    timestamp = peewee.BigIntegerField(primary_key=True)


class NumberOfProxiesToProcess(StatBaseModel):
    class Meta:
        db_table = "number_of_proxies_to_process"

    good_proxies = peewee.IntegerField(null=False)
    bad_proxies = peewee.IntegerField(null=False)
    dead_proxies = peewee.IntegerField(null=False)


class NumberOfCollectorsToProcess(StatBaseModel):
    class Meta:
        db_table = "number_of_collectors_to_process"

    value = peewee.IntegerField(null=False)


class ProcessorProxiesQueueSize(StatBaseModel):
    class Meta:
        db_table = "processor_proxies_queue_size"

    value = peewee.IntegerField(null=False)


db = peewee_async.Manager(raw_db)
# db.allow_sync()
