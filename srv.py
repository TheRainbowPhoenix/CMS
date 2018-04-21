import pickle
import logging
import logging.handlers
import struct
import sys
import socket
import threading

if sys.version_info[0] > 2:
    import socketserver as SocketServer
else:
    import SocketServer

HOSTNAME = '0.0.0.0'
PORT = 8833
TELNET_PORT = 8023
SDP_PORT = 4095  # Server Discovery Port
SDP_ADDRESS = "239.255.4.3"
# SDP_ADDRESS = "224.0.0.251"


# ==============================================================================
#  Generic Functions
#

def get_local_ip():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

# ==============================================================================
#  Classes Definition
#


class StreamHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        while True:
            chnk = self.connection.recv(4)
            if len(chnk) < 4:
                break
            stlen = struct.unpack('>L', chnk)[0]
            chnk = self.connection.recv(stlen)
            while len(chnk) < stlen:
                chnk += self.connection.recv(stlen - len(chnk))
            parsed = self.parse(chnk)
            register = logging.makeLogRecord(parsed)
            self.reg(register)

    def parse(self, data):
        return pickle.loads(data)

    def reg(self, register):
        if self.server.logname is None:
            name = self.server.logname
        else:
            name = register.name
        logger = logging.getLogger(name)
        logger.handle(register)


class TelnetHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        self.kill = 0
        self.welcome()
        while not self.kill:
            chnk = self.connection.recv(1024)
            if len(chnk) < 4:
                break
            # stlen = struct.unpack('>L', chnk)[0]
            # chnk = self.connection.recv(stlen)
            # while len(chnk) < stlen:
            #     chnk += self.connection.recv(stlen - len(chnk))
            if not self.parse(chnk):
                self.reg(chnk)
            # register = logging.makeLogRecord(parsed)
        self.connection.close()

    def ping(self, data):
        self.connection.send('Received {} bytes for {}\n'.format(len(data), self.client_address[0]).encode())

    def get(self, data):
        self.connection.send('{}\n'.format(self.kill).encode())

    def quit(self, data):
        self.kill = 1

    def parse(self, data):
        if data.decode("utf8").rstrip().split(' ')[0] in ('ping', 'quit', 'get'):
            getattr(self, data.decode("utf8").rstrip().split(' ')[0])(data)
            return 1
        return 0

    def reg(self, register):
        print('%s' % register)
        self.connection.send('[OK] '.encode() + register)

    def welcome(self):
        self.connection.send('Welcome !\n'.encode())


class SocketRecv(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def __init__(self, host=HOSTNAME,
                 port=PORT,
                 handler=StreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.kill = 0
        self.timeout = 1
        self.logname = None

    def loop_until_end(self):
        import select
        kill = 0
        while not kill:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                try:
                    self.handle_request()
                except:
                    self.close_request()
                    self.connection.close()
            kill = self.kill


class TelnetRecv(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def __init__(self, host=HOSTNAME,
                 port=TELNET_PORT,
                 handler=TelnetHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.kill = 0
        self.timeout = 1

    def loop_until_end(self):
        import select
        kill = 0
        while not kill:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            kill = self.kill


class SDPRecv(SocketServer.ThreadingUDPServer):
    allow_reuse_address = 1

    def __init__(self, host=SDP_ADDRESS,
                 port=SDP_PORT):
        self.socket = None
        self.create_socket(host, port)
        # SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.kill = 0
        self.timeout = 1
        self.ip = ''

    def create_socket(self, host, port):
        local_ip = get_local_ip()
        # socket.gethostbyname(socket.gethostname())
        #  TODO: Auto local ip Discovery

        self.ip = local_ip

        print(local_ip)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        req = socket.inet_aton(host) + socket.inet_aton(local_ip)

        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, req)

        if sys.platform.startswith("darwin"):
            self.socket.bind(('0.0.0.0', port))
        else:
            self.socket.bind((local_ip, port))

    def reply(self, host):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.bind(('0.0.0.0', SDP_PORT-1))
        # try:
        #     s.connect((host, SDP_PORT-1))
        # except Exception as e:
        #     print("Connection error : {}".format(e))

        lip = get_local_ip()

        s.sendto(lip.encode(), (host, SDP_PORT-1))
        print('sent')
        # s.sendall(bytes(self.ip.encode()))
        # data = s.recv(1024)
        # print(repr(data))
        # s.close()



    def loop_until_end(self):
        kill = 0
        while not kill:
            data, address = self.socket.recvfrom(4096)
            print("a")
            if len(data.decode().split('.'))==4:
                print("replying to {}".format(data))
                self.reply(data)
            print("%s says %s" % (address, data))
            kill = self.kill

def main():
    cms_format = logging.Formatter(
    '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
    '%(message)s',
    datefmt="[%d/%m/%Y %H:%M]")
    logging.basicConfig(format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
    tcpserver = SocketRecv()
    tlnserver = TelnetRecv()
    sdpserver = SDPRecv()
    # tlnserver.bind()
    print("starting on {}, {}, {}".format(PORT, TELNET_PORT, SDP_PORT))
    t1 = threading.Thread(target=tlnserver.loop_until_end)
    t2 = threading.Thread(target=tcpserver.loop_until_end)
    t3 = threading.Thread(target=sdpserver.loop_until_end)
    t1.start()
    t2.start()
    t3.start()


if __name__ == '__main__':
    main()
