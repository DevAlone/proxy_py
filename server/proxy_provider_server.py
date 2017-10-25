from core.models import Proxy
from server.api_request_handler import ApiRequestHandler

import asyncore
import socket
import threading
import logging
import re

_proxy_provider_server = None
_logger = logging.getLogger('proxy_py/server')
_logger.setLevel(logging.DEBUG)
debug_file_handler = logging.FileHandler('logs/server.debug.log')
debug_file_handler.setLevel(logging.DEBUG)
error_file_handler = logging.FileHandler('logs/server.error.log')
error_file_handler.setLevel(logging.ERROR)
error_file_handler = logging.FileHandler('logs/server.warning.log')
error_file_handler.setLevel(logging.WARNING)
info_file_handler = logging.FileHandler('logs/server.log')
info_file_handler.setLevel(logging.INFO)

_logger.addHandler(debug_file_handler)
_logger.addHandler(error_file_handler)
_logger.addHandler(info_file_handler)

_api_request_handler = ApiRequestHandler(_logger)


class RequestHandler(asyncore.dispatcher_with_send):
    MAX_REQUEST_SIZE = 1024  # 1 KB
    # TIMEOUT = 30
    TCP_REQUEST_THRESHOLD = 10

    def handle_read(self):
        try:
            client_address = self.socket.getpeername()

            data = self.recv(self.MAX_REQUEST_SIZE)
            if data:
                if len(data) < self.TCP_REQUEST_THRESHOLD:
                    for urlData in self.getUrls():
                        self.send(urlData)
                else:
                    method, url, headers, post_data = parse_http(data.decode('utf-8'))
                    if method is not None:
                        self.send(_api_request_handler.handle(client_address, method, headers, post_data))
                    else:
                        self.send(b"It's not a request\n")
        except:
            _logger.exception("Error in RequestHandler")
        finally:
            self.close()

    def getUrls(self):
        try:
            for proxy in Proxy.objects.all().filter(badProxy=False).order_by('uptime'):
                yield "{}\n".format(proxy.toUrl()).encode('utf-8')
        except:
            _logger.exception("Error in RequestHandler.getUrls(self)")


class ProxyProviderServer(asyncore.dispatcher):
    @staticmethod
    def get_proxy_provider_server(host, port, processor):
        global _proxy_provider_server
        if _proxy_provider_server is None:
            _proxy_provider_server = ProxyProviderServer(host, port, processor)
        return _proxy_provider_server

    def __init__(self, host, port, processor):
        super(ProxyProviderServer, self).__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.settimeout(1)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

        self._processor = processor
        self._thread = threading.Thread(target=self.worker)
        self._is_alive = False

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            _logger.info("Connection from {}".format(addr))
            handler = RequestHandler(sock)

    def start(self):
        self._is_alive = True
        self._thread.start()

    def stop(self):
        self._is_alive = False
        # TODO: stop asyncore loop

    def join(self):
        self._thread.join()

    def worker(self):
        while self._is_alive:
            try:
                asyncore.loop()
            except:
                _logger.exception("Error in ProxyProviderServer")


def parse_http(str_request):
    def split_lines(lines):
        buffer = ""
        for ch in lines:
            if ch == '\n':
                yield buffer
                buffer = ""
            elif ch != '\r':
                buffer += ch

        if buffer:
            yield buffer

    def split_by_first(line, ch):
        pos = line.find(ch)
        if pos != -1:
            return line[:pos], line[pos + 1:]
        else:
            return (line, '')


    method = None
    url = None
    headers = {}
    post_data = ""
    if str_request.startswith('get') or str_request.startswith('GET'):
        method = 'get'
    elif str_request.startswith('post') or str_request.startswith('POST'):
        method = 'post'
    else:
        return method, url, headers, post_data

    in_headers = True
    for i, line in enumerate(split_lines(str_request)):
        if i == 0:
            res = re.search(r'^[a-zA-Z]+\s+(.+)\s+', line)
            if res is not None:
                url = res.group(1)
        elif len(line) == 0:
            in_headers = False
        elif in_headers:
            key_val = split_by_first(line, ':')
            headers[key_val[0]] = key_val[1]
        else:
            post_data += line + '\n'

    return method, url, headers, post_data