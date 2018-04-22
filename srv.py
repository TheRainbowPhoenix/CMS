import pickle
import logging
import logging.handlers
import struct
import sys
import socket
import threading
import time

from CSettings import CSettings
from dataIO import fileIO

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

def LoadConf(file):
    Conf = fileIO("config/srv.json","r")

# ==============================================================================
#  Classes Definition
#

class Settings(CSettings):
    def pre_init(self):
        self.filename = 'srv'
        self.services = []
        self.s['services'] = self.services

    def file_checks(self, fs):
        if "services" not in fs:
            fileIO("config/{}.json".format(self.filename), "w", self.s)
        else:
            self.services = self.s["services"]

    def add_service(self, service):
        self.services.append(service)

    def remove_service(self, service):
        try:
            self.services.remove(service)
        except:
            return False

    def get_services(self):
        return self.services

    def pre_write(self):
        self.s['services'] = self.services

Config = Settings(CSettings)

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
        self.ps = "~"
        self.welcome()
        while not self.kill:
            self.connection.send('{} '.format(self.ps).encode())
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

    def HELP(self, data):
        data = data.decode("utf8","ignore").rstrip()
        if len(data.split(' ')) is not 1:
            pass
        else:
            out = """CMS V1.0 - Avaible commands\n\nHELP\n
  PING\t\tPing utility
  GET\t\tGet current settings
  SET\t\tChange current settings
  QUIT\t\tTerminate current session\n"""
            self.connection.send('{}\n'.format(out).encode())

    def PING(self, data):
        data = data.decode("utf8","ignore").rstrip()
        if len(data.split(' ')) is not 1:
            pt = False
            if len(data.split(' ')) > 2:
                if data.split(' ')[2].lower() in ['t', 'time']:
                    pt = True

            if data.split(' ')[1].isdigit():
                t0 = int(round(time.time() * 1000))
                for i in range(0,int(data.split(' ')[1])):
                    if pt and i%64==0:
                        self.connection.send('\n{} '.format(int(round(time.time() * 1000))).encode())
                    self.connection.send('.'.encode())
                t = int(round(time.time() * 1000)) - t0
                self.connection.send('\nSend {} bytes to {} in {} ms\n'.format(data.split(' ')[1], self.client_address[0], t).encode())
        else:
            out = "CMS PING utility : Get the time for sending n bytes\n\nPING [count] [time | t]\n\n  count \tNumber of bytes to send\n  time | t \tprint epoch time every 64 bytes\n"
            self.connection.send('{}\n'.format(out).encode())

    def GET(self, data):
        data = data.decode("utf8","ignore").rstrip()
        if len(data.split(' ')) is not 1:
            if data.split(' ')[1].lower() == 'services':
                out = 'Running : '+', '.join(Config.get_services())
                self.connection.send('{}\n'.format(out).encode())
            elif data.split(' ')[1].lower() == 'all':
                out = 'Server\n'
                out += '  IP : \t\t{}\n'.format(Config.server)
                out += '  Port : \t{}\n'.format(Config.port)
                out += '\nSDP\n'
                out += '  Address : \t{}\n'.format(Config.sdp_address)
                out += '  Port : \t{}\n'.format(Config.sdp_port)
                out += '\nServices\n'
                out += '  Running : \t'+', '.join(Config.get_services())+'\n'
                out += '  Avaible : \t'+', '.join(Config.get_s()['services'])+'\n'
                self.connection.send('{}\n'.format(out).encode())
        else:
            out = "CMS GET utility : Get informations about system\n\nGET [services | all]\n\n  services\tPrint running services\n  all\t\tprint current config\n"
            self.connection.send('{}\n'.format(out).encode())

    def SET(self, data):
        # TODO: If logged as admin
        data = data.decode("utf8","ignore").rstrip()
        if len(data.split(' ')) is not 1:
            if data.split(' ')[1].lower() == 'server':
                if len(data.split(' ')) > 2:
                    if data.split(' ')[2].lower() == 'ip':
                        if len(data.split(' ')) > 3:
                            if data.split(' ')[3].lower() is not '':
                                Config.server = '{}'.format(data.split(' ')[3])
                        else:
                            out = "SET SERVER IP [x.x.x.x | hostname]\n  x.x.x.x\t\tIPv4 Address\n  hostname\t\tHost name (like localhost)"
                            self.connection.send('{}\n'.format(out).encode())
                    elif data.split(' ')[2].lower() == 'port':
                        if len(data.split(' ')) > 3:
                            if data.split(' ')[3].lower().isdigit():
                                Config.port = '{}'.format(data.split(' ')[3])
                        else:
                            out = "SET SERVER PORT x\n  x\t\tDesired port (numeric)"
                            self.connection.send('{}\n'.format(out).encode())
                    else:
                        out = "SET SERVER [PORT | IP]\n  PORT\t\tChange server port\n  IP\t\tChange server ip"
                        self.connection.send('{}\n'.format(out).encode())
                else:
                    out = "SET SERVER [PORT | IP]\n  PORT\t\tChange server port\n  IP\t\tChange server ip"
                    self.connection.send('{}\n'.format(out).encode())
            elif data.split(' ')[1].lower() == 'sdp':
                if len(data.split(' ')) > 2:
                    if data.split(' ')[2].lower() == 'address':
                        if len(data.split(' ')) > 3:
                            if data.split(' ')[3].lower() is not '':
                                Config.sdp_address = '{}'.format(data.split(' ')[3])
                        else:
                            out = "SET SDP ADDRESS x.x.x.x\n  x.x.x.x\t\tIPv4 Multicast Address"
                            self.connection.send('{}\n'.format(out).encode())
                    elif data.split(' ')[2].lower() == 'port':
                        if len(data.split(' ')) > 3:
                            if data.split(' ')[3].lower().isdigit():
                                Config.sdp_port = '{}'.format(data.split(' ')[3])
                        else:
                            out = "SET SDP PORT x\n  x\t\tDesired port (numeric)"
                            self.connection.send('{}\n'.format(out).encode())
                    else:
                        out = "SET SDP [PORT | ADDRESS]\n  PORT\t\tChange SDP port\n  ADDRESS\t\tChange SDP address"
                        self.connection.send('{}\n'.format(out).encode())
                else:
                    out = "SET SDP [PORT | ADDRESS]\n  PORT\t\tChange SDP port\n  ADDRESS\t\tChange SDP address"
                    self.connection.send('{}\n'.format(out).encode())
            elif data.split(' ')[1].lower() == 'services':
                if len(data.split(' ')) > 2:
                    # TODO: Service manager
                    # Settings.services = running services
                    # Settings.s['services'] = avaible services (at startup)
                    if data.split(' ')[2].lower() == 'start':
                        pass
                    elif data.split(' ')[2].lower() == 'stop':
                        pass
                    elif data.split(' ')[2].lower() == 'restart':
                        pass
                    else:
                        out = "SET SERVICES [START | STOP | RESTART]\n  START\t\tStart desired service\n  STOP\t\tStop desired service\n  RESTART\t\tRestart desired service"
                        self.connection.send('{}\n'.format(out).encode())
                else:
                    out = "SET SERVICES [START | STOP | RESTART]\n  START\t\tStart desired service\n  STOP\t\tStop desired service\n  RESTART\t\tRestart desired service"
                    self.connection.send('{}\n'.format(out).encode())

            else:
                out = "SET [SERVER | SDP | SERVICES]\n  SERVER\tChange server settings\n  SDP\t\tChange SDP settigs\n  SERVICES\tManage running services"
                self.connection.send('{}\n'.format(out).encode())
        else:
            out = "CMS SET utility : Change current settings\n\n"
            out += "SET [SERVER [PORT | IP ] | SDP [PORT | ADDRESS] | SERVICES [START | STOP | RESTART]]\n\n"
            out += "  SERVER\tChange server settings\n"
            out += "    PORT\tChange server port\n"
            out += "    IP\t\tChange server ip\n\n"
            out += "  SDP\t\tChange SDP settigs\n"
            out += "    PORT\tChange SDP port\n"
            out += "    ADDRESS\tChange SDO address\n\n"
            out += "  SERVICES\tManage running services\n"
            out += "    START\tStart service\n"
            out += "    STOP\tStop service\n"
            out += "    RESTART\tRestart service\n"
            self.connection.send('{}\n'.format(out).encode())

    def QUIT(self, data):
        self.kill = 1

    def parse(self, data):
        if data.decode("utf8","ignore").rstrip().split(' ')[0] in ('PING', 'QUIT', 'GET', 'SET', 'HELP'):
            getattr(self, data.decode("utf8").rstrip().split(' ')[0])(data)
            return 1
        return 0

    def reg(self, register):
        register = register.decode("utf-8","ignore").rstrip()
        print('%s' % register)
        self.connection.send('Unknown command "{}"\n'.format(register).encode())

    def welcome(self):
        #TODO: banner
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

    def kill(self):
        self.kill=1

    def loop_until_end(self):
        import select
        kill = 0
        Config.add_service('Socket')
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
        Config.remove_service('Socket')


class TelnetRecv(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def __init__(self, host=HOSTNAME,
                 port=TELNET_PORT,
                 handler=TelnetHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.kill = 0
        self.timeout = 1

    def kill(self):
        self.kill=1

    def loop_until_end(self):
        import select
        kill = 0
        Config.add_service('Telnet')
        while not kill:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            kill = self.kill
        Config.remove_service('Telnet')


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

    def kill(self):
        self.kill=1

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
        Config.add_service('SDP')
        while not kill:
            data, address = self.socket.recvfrom(4096)
            print("a")
            if len(data.decode().split('.'))==4:
                print("replying to {}".format(data))
                self.reply(data)
            print("%s says %s" % (address, data))
            kill = self.kill
        Config.remove_service('SDP')


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
