from dataclasses import dataclass

from .protocol import Protocol


@dataclass(frozen=True)
class CheckProxyMessage:
    protocol: Protocol
    login: str
    password: str
    hostname: str
    port: int

    def to_url(self) -> str:
        return proxy_to_url(self.protocol, self.login, self.password, self.hostname, self.port)


@dataclass(frozen=True)
class ProxyCheckingResult:
    check_proxy_message: CheckProxyMessage
    does_work: bool
    # response time in seconds
    response_time: float
    # TODO: maybe some more fields like exception why timed out,
    #  which checkers checked it, ip, location, etc


def proxy_to_url(protocol: Protocol, login: str, password: str, hostname: str, port: int) -> str:
    auth_data = ""
    if login or password:
        auth_data = f"{login}:{password}@"

    url = f"{protocol.name}://{auth_data}{hostname}:{port}"

    return url
