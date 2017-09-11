# TODO: refactor this shit

from socketserver import BaseRequestHandler, TCPServer
from threading import Thread
import time
from core.models import Proxy

try:
    import pydevd
except:
    pass

serverThread = None
host = None
port = None
collector = None
server = None
isAlive = True
serverRunning = False


class TCPHandler(BaseRequestHandler):
    def handle(self):
        result = ""
        try:
            for proxy in Proxy.objects.all().filter(badProxy=False):
                result += proxy.toUrl() + "\n"
        except:
            pass  # TODO: log it
        self.request.sendall(result.encode())
        # self.data = self.request.recv(1024).strip()
        # self.request.sendall(self.data.upper())

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


def runServer(lcollector, lhost = "localhost", lport = 55555):
    global collector, serverThread, host, port
    host = lhost
    port = lport
    collector = lcollector
    serverThread = Thread(target=_runServer)
    serverThread.start()


def stopServer():
    global isAlive, server
    isAlive = False
    if server is not None and serverRunning:
        server.shutdown()
    serverThread.join()
