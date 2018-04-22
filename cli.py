# -*- coding: utf-8 -*-
#
# CMS Client Monitoring Service

from importlib import import_module
import os
import sys
import time
import logging
import logging.handlers
import traceback
import datetime
import socket
import subprocess
import threading
sys.path.insert(0, "lib")
import CSettings
from CSettings import CSettings
from dataIO import fileIO

# Thoses values are here if CSettings got a problem while import, as default values

SERVER = 'localhost'
PORT = 8833
SDP_PORT = 4095  # Server Discovery Port
SDP_ADDRESS = "239.255.4.6"

def Get_SDP_ip(Config):
    a, p = Config.get_sdp_server()
    SDPTst = SDPSnd(a, p)
    c = 0
    SDPL = threading.Thread(SDPListener(SDPTst, Config))
    SDPL.start()
    # time.sleep(8)
    SDPL.join()


# ==============================================================================
#  Generic Functions
#

def get_local_ip():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


# =============================================================================
# Server Discovery Stuff
#


class SDPSnd():
    allow_reuse_address = 1

    def __init__(self, host=SDP_ADDRESS,
                 port=SDP_PORT):
        self.socket = None
        self.host = host
        self.port = port
        self.create_socket()
        # SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.kill = 0
        self.timeout = 1

    def create_socket(self):
        self.local_ip = get_local_ip()
        # socket.gethostbyname(socket.gethostname())
        #  TODO: Auto local ip Discovery

        print(self.local_ip)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.local_ip))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        req = socket.inet_aton(self.host) + socket.inet_aton(self.local_ip)

        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, req)

        if sys.platform.startswith("darwin"):
            self.socket.bind(('0.0.0.0', self.port))
        else:
            self.socket.bind((self.local_ip, self.port))

    def resolve(self):
        message = "{}".format(self.local_ip)
        self.socket.sendto(message.encode(), (self.host, self.port))
        print("send")
        time.sleep(8)


class Settings(CSettings):
    def pre_init(self):
        self.filename = 'cli'

    def file_checks(self, fs):
        if "server" not in fs:
            if "sdp" not in fs:
                print("Invalid file, recreating")
                fileIO("config/{}.json".format(self.filename), "w", self.s)
            else:
                print("Resolving server ip ...")
                self.get_SDP_ip()
                if "server" not in self.s:
                    self.set_server(self.server)

    def get_SDP_ip(self):
        Get_SDP_ip(self)

    def get_server(self):
        return self.server

    def get_port(self):
        return self.port

    def get_sdp_server(self):
        return (self.sdp_address, self.sdp_port)

    def get_sdp_port(self):
        return self.sdp_address

    def set_server(self, server):
        self.s["server"] = server
        self.s["port"] = self.port
        self.server = server
        self.write_config()


class CSDPListener():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.s.bind(('0.0.0.0', Config.get_sdp_port()-1))
        self.s.listen(10)
        cn, ad = self.s.accept()
        data = cn.revc(1024)
        if data:
            cn.send('OK')
            print(data)
            self.s.shutdown(1)
            close()
        else:
            print("killing")
            self.s.shutdown(1)
            close()
    def close(self):
        self.s.close()

def Tprocess(cn, ip):
    InLoop = True
    while InLoop:
        data = cn.revc(1024).decode("utf8","ignore").rstrip()
        if len(data.split('.'))==4:
            print("Server ip is {}".format(data))
            cn.close()
            InLoop=False

def SDPListener(SDPTst,Config, c=4):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("socket created")
    try:
        s.bind(('0.0.0.0', 4094))
    except:
        print("bind failed")
    print("listening")
    # s.settimeout(8.0)
    try:
        print("SDP Request send, waiting for a reply from the server . . .")
        while c>0:
            SDPTst.resolve()
            data, ad = s.recvfrom(1024)
            if data:
                if len(data.decode().split('.'))==4:
                    print("Got server adress ! It is {}".format(data.decode()))
                    Config.set_server(data.decode())
                    print(Config.get_s())
                    s.shutdown(1)
                    s.close()
                    c=0
            print(data)
            c-=1
            # data = cn.revc(1024)
            # if data:
            #     cn.send('OK')
            #     print(data)
            #     break
    except:
        print("[E] Connexion timed out, retrying . . .")
        pass
    s.close()

# =============================================================================
# logging Stuff
#

Config = Settings(CSettings)
print(Config.get_server())
print(Config.get_s())

logger = logging.getLogger("CMS")
logger.setLevel(logging.INFO)

cms_format = logging.Formatter(
'%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
'%(message)s',
datefmt="[%d/%m/%Y %H:%M]")

stdout_handler = logging.StreamHandler(sys.stdout) # TODO: Mute
stdout_handler.setFormatter(cms_format)

file_handler = logging.handlers.RotatingFileHandler(
filename='logs/cms.log', encoding='utf-8', mode='a',
maxBytes=10**7, backupCount=5)
file_handler.setFormatter(cms_format)

print(Config.get_server(), Config.get_port())

socket_handler = logging.handlers.SocketHandler(Config.get_server(), Config.get_port())  # TODO: Change this ! (Server)
#socket_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(socket_handler)
logger.addHandler(file_handler)

logger.debug('Quick zephyrs blow, vexing daft Jim.')
logger.info('How quickly daft jumping zebras vex.')
logger.warning('Jail zesty vixen who grabbed pay from quack.')
logger.error('The five boxing wizards jump quickly.')


def dexec(command):
    os.system(" ".join((sys.executable, __file__, action)))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ('start', 'stop', 'restart'):
            dm = ClientLoop('/tmp/cli.pid', verbose=1)
            getattr(dm, arg)()
        else:
            sys.exit(0)
