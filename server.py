from socketserver import BaseRequestHandler, TCPServer
from threading import Thread
import time

serverThread = None
host = None
port = None
collector = None

class TCPHandler(BaseRequestHandler):
    def handle(self):
        result = ""
        for proxy in collector.proxies:
            result += proxy.toUrl() + "\n"
        self.request.sendall(result.encode())
        # self.data = self.request.recv(1024).strip()
        # self.request.sendall(self.data.upper())

def _runServer():
    while True:
        try:
            server = TCPServer((host, port), TCPHandler)
            server.serve_forever()
        except:
            time.sleep(5)


def runServer(lcollector, lhost = "localhost", lport = 55555):
    global collector, serverThread, host, port
    host = lhost
    port = lport
    collector = lcollector
    serverThread = Thread(target=_runServer)
    serverThread.start()