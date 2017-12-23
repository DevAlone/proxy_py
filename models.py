from proxy_py import settings
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, SmallInteger, BigInteger, UniqueConstraint
from sqlalchemy.orm import sessionmaker


engine = create_engine(*settings.DATABASE_CONNECTION_ARGS, **settings.DATABASE_CONNECTION_KWARGS)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Proxy(Base):
    __tablename__ = "proxies"
    __table_args__ = (
        UniqueConstraint("_protocol", "auth_data", "domain", "port"),
    )

    PROTOCOLS = (
        'http',
        'socks4',
        'socks5',
    )

    id = Column(Integer, primary_key=True)
    _protocol = Column(SmallInteger, nullable=False)
    domain = Column(String(128), nullable=False)
    port = Column(Integer, nullable=False)
    auth_data = Column(String(64), default="", nullable=False)

    last_check_time = Column(Integer, default=0)
    checking_period = Column(Integer, default=settings.MIN_PROXY_CHECKING_PERIOD, nullable=False)
    number_of_bad_checks = Column(Integer, default=0)
    uptime = Column(Integer, nullable=True, default=None)
    # in microseconds
    response_time = Column(Integer, nullable=True, default=None)

    @property
    def address(self):
        return self.to_url()

    @property
    def protocol(self):
        return self.PROTOCOLS[int(self._protocol)]

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = self.PROTOCOLS.index(protocol)

    @property
    def bad_proxy(self):
        return self.number_of_bad_checks > 0

    def to_url(self, protocol=None):
        address = protocol if protocol is not None else self.PROTOCOLS[int(self._protocol)]
        address += "://"
        if self.auth_data:
            address += self.auth_data + "@"

        address += "{}:{}".format(self.domain, self.port)

        return address

    def __str__(self):
        return self.to_url()

    __repr__ = __str__


class ProxyCountItem(Base):
    __tablename__ = "proxy_count_items"
    timestamp = Column(Integer, primary_key=True)
    good_proxies_count = Column(Integer, nullable=False)
    bad_proxies_count = Column(Integer, nullable=False)
    dead_proxies_count = Column(Integer, nullable=False)


# class Collector(Base):
#     __tablename__ = "collectors"
#     id = Column(Integer, primary_key=True)
#     processing_period = Column(Integer, nullable=False)
#     last_process_time = Column(Integer, nullable=False)
#     last_process_proxies_count = Column(Integer, nullable=False, default=0)
#     last_process_new_proxies_count = Column(Integer, nullable=False, default=0)


Base.metadata.create_all(engine)

session = Session()