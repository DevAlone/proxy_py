import socket
import time
from threading import Thread
import random

proxies = []
currentProxyIndex = 0
updatingThread = None
isAlive = True

def getNextProxy(forceIpChanging):
    global currentProxyIndex, proxies
    if forceIpChanging or random.randint(0, 100) < 50:
        currentProxyIndex += 1
    if currentProxyIndex >= len(proxies):
        currentProxyIndex = 0
    return proxies[currentProxyIndex]

def _worker():
    global proxies, isAlive
    while isAlive:
        try:
            sock = socket.socket()
            sock.connect(('localhost', 55555))
            sock.sendall(b'')
            data = b''
            while True:
                prev_size = len(data)
                data += sock.recv(1024)
                if prev_size == len(data):
                    break
            str_data = data.decode()
            if len(str_data) > 0:
                proxies.clear()
                proxies.extend(str_data.splitlines())
        except:
            print('error during getting proxies')
        print('proxies count is ' + str(len(proxies)))
        time.sleep(10)


def init():
    global updatingThread
    updatingThread = Thread(target=_worker)
    updatingThread.start()


def clean():
    global isAlive, updatingThread
    isAlive = False
    updatingThread.join()
