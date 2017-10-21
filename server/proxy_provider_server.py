# TODO: refactor this shit
# TODO: add logging

from server.api_request_handler import ApiRequestHandler

import socket
import time
from threading import Thread
from socketserver import BaseRequestHandler, TCPServer
from core.models import Proxy


try:
    import pydevd
except:
    pass

serverThread = None
host = None
port = None
processor = None
server = None
isAlive = True
serverRunning = False


class TCPHandler(BaseRequestHandler):
    MAX_REQUEST_SIZE = 1024 # 1 KB
    TIMEOUT = 30
    def handle(self):
        self.request.settimeout(self.TIMEOUT)

        try:
            data = self.request.recv(self.MAX_REQUEST_SIZE)
            if len(data) > 5:
                resp = ApiRequestHandler().handle(data)
            else:
                resp = self.getUrls()

            self.request.sendall(resp)
        except socket.timeout:
            self.request.sendall(b'Hurry up!\n')
        except Exception as ex:
            raise ex
            print('Some error in server: {}'.format(ex))
        except:
            print('Some error in server')

    def getUrls(self):
        result = ""
        try:
            for proxy in Proxy.objects.all().filter(badProxy=False).order_by('uptime'):
                result += "{}\n".format(proxy.toUrl())
        except:
            pass  # TODO: log it
        return result.encode()


def _runServer():
    global server, serverRunning
    TCPServer.allow_reuse_address = True
    while isAlive:
        serverRunning = False
        try:
            server = TCPServer((host, port), TCPHandler)
            serverRunning = True
            server.serve_forever()
        except Exception as ex:
            time.sleep(5)
        except:
            time.sleep(5)


def runServer(lprocessor, lhost = "localhost", lport = 55555):
    global processor, serverThread, host, port
    host = lhost
    port = lport
    processor = lprocessor
    serverThread = Thread(target=_runServer)
    serverThread.daemon = True
    serverThread.start()


def stopServer():
    global isAlive, server
    isAlive = False
    if server is not None and serverRunning:
        server.shutdown()
    # serverThread.join()
