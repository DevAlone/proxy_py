from proxy_py import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, SmallInteger, UniqueConstraint
from sqlalchemy.orm import sessionmaker


engine = create_engine(*settings.DATABASE_CONNECTION_ARGS, **settings.DATABASE_CONNECTION_KWARGS)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Proxy(Base):
    __tablename__ = "proxies"
    __table_args__ = (
        UniqueConstraint("raw_protocol", "auth_data", "domain", "port"),
    )

    PROTOCOLS = (
        'http',
        'socks4',
        'socks5',
    )

    id = Column(Integer, primary_key=True)
    raw_protocol = Column(SmallInteger, nullable=False)
    domain = Column(String(128), nullable=False)
    port = Column(Integer, nullable=False)
    auth_data = Column(String(64), default="", nullable=False)

    checking_period = Column(Integer, default=settings.MIN_PROXY_CHECKING_PERIOD, nullable=False)
    last_check_time = Column(Integer, default=0)
    number_of_bad_checks = Column(Integer, default=0)
    uptime = Column(Integer, nullable=True, default=None)
    bad_uptime = Column(Integer, nullable=True, default=None)
    # in microseconds
    response_time = Column(Integer, nullable=True, default=None)

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


class ProxyCountItem(Base):
    __tablename__ = "proxy_count_items"
    timestamp = Column(Integer, primary_key=True)
    good_proxies_count = Column(Integer, nullable=False)
    bad_proxies_count = Column(Integer, nullable=False)
    dead_proxies_count = Column(Integer, nullable=False)


class CollectorState(Base):
    __tablename__ = "collector_states"
    id = Column(Integer, primary_key=True)
    # python module name
    identifier = Column(String, unique=True)
    processing_period = Column(Integer, nullable=False)
    last_processing_time = Column(Integer, nullable=False)
    last_processing_proxies_count = Column(Integer, nullable=False, default=0)
    last_processing_new_proxies_count = Column(Integer, nullable=False, default=0)
    data = Column(String, nullable=True, default=None)


Base.metadata.create_all(engine)

session = Session()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()

    return instance
