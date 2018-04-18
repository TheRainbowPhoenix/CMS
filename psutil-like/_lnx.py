""" Psutil - Like library // Linux Support """

import subprocess
import datetime
import os
import time
import threading
import struct
from time import sleep
from collections import namedtuple

_timer = getattr(time, 'monotonic', time.time)

def space_s(s):
    while '  ' in s:
        s=s.replace('  ', ' ')
    return s


def v_mem():
    mem = [0,0,0,0,0]     # total, available, percent, used, free
    rmem = {}
    try:
        with open('/proc/meminfo', "rb") as f:
            for l in f:
                e = l.split()
                rmem[e[0].decode()[:-1]] = int(e[1]) * 1024
    except:
        return [-1 for i in mem]
    try:
        mf = rmem['MemFree']
        mc = rmem['Cached']
        mt = rmem['MemTotal']
        mb = rmem['Buffers']
        ma = mf+mc
        # mu = mt - mf - mc - mb
        mu = mt - mf
        mp = round(100-ma*100.0/mt,1)
        mem = [mt, ma, mp, mu, mf]
    except KeyError:
        try:
            fm = [int(i)*1024 for i in subprocess.check_output(["free"]).decode('utf-8', 'ignore').split('\n')[1].split()[1:]]
            mt = fm[0]
            ma = fm[0]-fm[1]
            mf = fm[4]
            mu = fm[0]-fm[2]
            mp = round(100-ma*100.0/mt,1)
            mem = [mt, ma, mp, mu, mf]
        except:
            return [-1 for i in mem]
    return mem


def count_cpu():
    c = 0
    try:
        with open('/proc/cpuinfo') as f:
            for l in f:
                if 'processor' in l:
                    c+=1
    except:
        return -1
    return c

def cpu_percent(Freq=100.0):
    u = 0.0
    li = lt = 0
    c=2
    def timer():
        return _timer() * count_cpu()

    lid = ltl = 1
    try:
        while c>0:
            with open('/proc/stat') as f:
                l = [float(column) for column in f.readline().strip().split()[1:]]
            id, tl = l[3], sum(l)
            idd, tld = id - lid, tl - ltl
            lid, ltl = id, tl
            try:
                u = 100.0 * (1.0 - idd / tld)
            except ZeroDivisionError:
                u =0.0
            sleep(float(count_cpu())/Freq)
            c-=1
        return round(u,1)
    except:
        return -1

def disk_partitions(all=False):
    fsd = []
    f = open("/proc/filesystems", "r")
    for l in f:
        if not l.startswith("nodev"):
            fsd.append(l.strip())

    r = []
    try:
        with open('/etc/mtab', "r") as f:
            for l in f:
                if not all and l.startswith('none'):
                    continue
                l = l.split()
                device = l[0]
                mountpoint = l[1]
                fstype = l[2]
                opts = l[3]
                if not all and fstype not in fsd:
                    continue
                if device == 'none':
                    device = ''
                dp =  namedtuple('sdiskpart', ['device', 'mountpoint', 'fstype', 'opts'])
                r.append(dp(device, mountpoint, fstype, opts))
    except:
        try:
            with open('/proc/mounts') as f:
                for l in f:
                    if l.startswith('/dev/'):
                        dp = namedtuple('sdiskpart', ['device', 'mountpoint', 'fstype', 'opts'])
                        l = l.split()
                        r.append(dp(l[0],l[1],l[2],l[3]))
        except:
            pass
    # mountfile = ['/etc/mtab', '/etc/mnttab', '/proc/mounts']

    return r

def disk_usage(disk):
    # total, used, free, percent
    du = [0, 0, 0, 0]
    try:
        s = os.statvfs(disk)
        free = (s.f_bavail * s.f_frsize)
        total = (s.f_blocks * s.f_frsize)
        used = (s.f_blocks - s.f_bfree) * s.f_frsize
        try:
            percent = ret = round(100*(float(used)/total),1)
        except ZeroDivisionError:
            percent = 0
        du = [total, used, free, percent]
    except:
        du = [-1,-1,-1,-1]
    return du

def utmp_parse(fname):
    r = []
    f = open(fname, 'rb')
    while True:
        b = f.read(struct.calcsize('hi32s4s32s256shhiii4i20x'))
        if not b:
            break
        d = struct.unpack('hi32s4s32s256shhiii4i20x', b)
        d = [(lambda s: str(s).split("\0", 1)[0])(i) for i in d]
        if d[0] != '0' and d[4] not in ('','LOGIN','reboot','shutdown','runlevel'):
            r.append(d)
    f.close()
    r.reverse()
    return r

def users():
    r = []
    try:
        us = utmp_parse('/var/run/utmp')
        su = namedtuple('suser', ['name', 'terminal', 'host', 'started'])
        for i in us:
            r.append(su(i[4], i[2], i[3], float(i[9])))
    except:
        pass
    return r

def pids():
    r = []
    try:
        r = [int(p) for p in os.listdir('/proc') if p.isdigit()]
    except:
        pass
    return r
