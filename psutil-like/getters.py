import socket
import sys
from datetime import date, datetime
import platform
import subprocess

try:
	import psutil
	NO_PS = 0
except:
	import psutill as psutil
	NO_PS = 1
	
class Getter:
    def __init__(self):
        self.cpu = None
        self.mem = None
        self.dis = None
        self.ip = None
        self.memory_available = None
        self.disk_available = None
        self.users = None
        self.procc = None

    def getCpu(self):
        self.cpu = str(psutil.cpu_percent())

    def getMem(self):
        self.mem = str(psutil.virtual_memory().percent)

    def getDis(self):
        self.dis = str(psutil.disk_usage(psutil.disk_partitions()[0].mountpoint).percent)

    def getLIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            self.ip = s.getsockname()[0]
        except Exception:
            self.ip = '127.0.0.1'
        finally:
            s.close()

    def getUsers(self):
        self.users = [i.name for i in psutil.users()]

    def getProcc(self):
        self.procc = len(psutil.pids())

    def refresh(self):
        self.getCpu()
        self.getMem()
        self.getDis()
        self.getLIP()
        self.getProcc()
        self.getUsers()

    def get(self):
        rep = {'cpu': self.cpu, 'mem': self.mem, 'dis': self.dis, 'ip': self.ip, 'memory_available': self.memory_available, 'disk_available': self.disk_available, 'users': self.users, 'procc': self.procc}
        return rep

# g = Getter()
# g.refresh()
# print(g.get())