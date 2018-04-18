""" Psutil - Like library // Windows Support """

import subprocess
import datetime
from collections import namedtuple

# wmic computersystem get TotalPhysicalMemory
# wmic OS get FreePhysicalMemory
# wmic cpu get loadpercentage
# WMIC LOGICALDISK GET Size,FreeSpace,Name
# wmic netlogin get name, lastlogon
# wmic process get Processid

def space_s(s):
    while '  ' in s:
        s=s.replace('  ', ' ')
    return s

def v_mem():
    mem = [0,0,0,0,0]
    try:
        mem[0] = int(subprocess.check_output(["bin\wmic.exe","computersystem","get","TotalPhysicalMemory"]).split()[1].decode())
    except:
        mem[0] = -1

    try:
        mem[4] = int(subprocess.check_output(["bin\wmic.exe","OS","get","FreePhysicalMemory"]).split()[1].decode())*1000
    except:
        mem[4] = -1

    mem[1] = mem[4]

    if (mem[0] != -1 and mem[4] != -1):
        mem[3] = mem[0] - mem[4]
        mem[2] = round(100-(mem[4]*100/mem[0]),1)
    else:
        mem[2] = -1
        mem[3] = -1
    return mem

def cpu_percent():
    try:
        u = int(subprocess.check_output(["bin\wmic.exe","cpu","get","loadpercentage"]).split()[1].decode())
    except:
        u = -1
    return u

def disk_partitions():
    r = []
    try:
        id=[i.decode() for i in subprocess.check_output(["bin\wmic.exe","logicaldisk","get","DeviceID"]).split()[1:]]
        fs = [i.split() for i in subprocess.check_output(["bin\wmic.exe","logicaldisk","get","FileSystem"]).split(b'\n')[1:-1]]
        op = [space_s(i).rstrip() for i in subprocess.check_output(["bin\wmic.exe","logicaldisk","get","Description"]).decode('utf-8', 'ignore').split('\n')[1:-1]]

        if id != []:
            for i in range(0, len(id)):
                dp = namedtuple('sdiskpart', ['device', 'mountpoint', 'fstype', 'opts'])
                fst = fs[i][0].decode() if fs[i] != [] else ''
                opt = 'fixed' if 'local' in op[i] else 'removable'
                if 'dis' in op[i].lower():opt = 'rw,'+opt
                if 'CD' in op[i]: opt = 'cdrom'
                r.append(dp(id[i]+'\\',id[i]+'\\', fst, opt))
                # sdiskpart (device='C:\\', mountpoint='C:\\', fstype='NTFS', opts='rw,fixed')
    except:
        return ['']
    return r

def disk_usage(drive):
    du = [0, 0, 0, 0]
    try:
        for i in subprocess.check_output(["bin\wmic.exe","logicaldisk","get","Size,FreeSpace,Name"]).decode().split('\n')[1:]:
            if drive.replace("\\", "") in i:
                p = i.split()
                du = [int(p[2]), int(p[2])-int(p[0]), int(p[0]), round(100-(int(p[0])*100/int(p[2])),1)]
    except:
        du = [-1,-1,-1,-1]
    return du

def users():
    r = []
    try:
        now = str(datetime.datetime.now()).split('.')[0].translate(''.maketrans("","", '- :'))
        lt = [i.split() for i in subprocess.check_output(["bin\wmic.exe","netlogin","get","lastlogon"]).decode('utf-8','ignore').split('\n')][1:-1]
        us = [i.rstrip() for i in subprocess.check_output(["bin\wmic.exe","netlogin","get","name"]).decode('utf-8','ignore').split('\n')[1:-1]]
        for i in range(0, len(lt)):
            su = namedtuple('suser', ['name', 'terminal', 'host', 'started'])
            ltt = int(now)-int(lt[1][0].split('.')[0]) if lt[i] != [] else -1
            ust = us[i].split('\\')[-1]
            r.append(su(ust, None, 'localhost', ltt))
    except:
        pass
    return r

def pids():
    r = []
    try:
        r = [int(i) for i in subprocess.check_output(["bin\wmic.exe","process","get","Processid"]).decode('utf-8','ignore').split()[1:]]
    except:
        pass
    return r

# wmic process get Caption,Processid
