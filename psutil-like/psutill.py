""" Psutil - Like library """

import platform
import os
import sys
from collections import namedtuple

if platform.system()=='Windows':
    import _win as pext
elif platform.system()=='Linux':
    import _lnx as pext
else:
    import _lnx as pext


svmem = namedtuple('svmem', ['total', 'available', 'percent', 'used', 'free'])
sdu = namedtuple('sdiskusage', ['total', 'used', 'free', 'percent'])

def virtual_memory():
    total = available = percent = used = free = 0
    total, available, percent, used, free = pext.v_mem()
    return svmem(total, available, percent, used, free)

def cpu_percent():
    return round(pext.cpu_percent(), 1)

def disk_partitions():
    return pext.disk_partitions()

def disk_usage(drive):
    total, used, free, percent = pext.disk_usage(drive)
    return sdu(total, used, free, percent)

def users():
    return pext.users()

def pids():
    return pext.pids()

print(virtual_memory())
print(cpu_percent())
print(disk_partitions())
print(disk_partitions()[0].mountpoint)
print(str(disk_usage(disk_partitions()[0].mountpoint)))
print(users())
print(pids())
