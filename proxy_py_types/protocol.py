import enum


class Protocol(enum.Enum):
    http = enum.auto()
    socks4 = enum.auto()
    socks5 = enum.auto()
