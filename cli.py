# -*- coding: utf-8 -*-
#
# CMS Client Monitoring Service

from importlib import import_module
from daemon import Daemon
import os
import sys
import time
import logging
import logging.handlers
import traceback
import datetime
import socket
import subprocess
sys.path.insert(0, "lib")


SERVER = 'localhost'
PORT = 8833
SDP_PORT = 4095  # Server Discovery Port
SDP_ADDRESS = "239.255.4.3"

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
        self.local_ip = socket.gethostbyname(socket.gethostname())
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


SDPTst = SDPSnd()
SDPTst.resolve()

# =============================================================================
# logging Stuff
#

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

socket_handler = logging.handlers.SocketHandler(SERVER, PORT)  # TODO: Change this ! (Server)
#socket_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(socket_handler)
logger.addHandler(file_handler)

logger.debug('Quick zephyrs blow, vexing daft Jim.')
logger.info('How quickly daft jumping zebras vex.')
logger.warning('Jail zesty vixen who grabbed pay from quack.')
logger.error('The five boxing wizards jump quickly.')


class ClientLoop(Daemon):
    def __init__(self, *args, **kwargs):
        super(ClientLoop, self).__init__(*args, **kwargs)

    def run(self):
        while True:
            self.main()

    def main():
        try:
            while True:
                time.sleep(1)
        except:
            return

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
