import settings

from .proxy_provider_server import ProxyProviderServer


def main():
    proxy_provider_server = ProxyProviderServer(
        settings.server.hostname,
        settings.server.port,
    )

    return proxy_provider_server.start()
