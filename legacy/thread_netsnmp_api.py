#!/usr/bin/env python3

import sys
import threading
import time
from queue import Queue
from netsnmp import *


def worker_loop(i, q):

    vars      = SNMPVarlist('.1.3.6.1.2.1.1.1.0')
    #vars      = SNMPVarlist('.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0', '.1.3.6.1.2.1.1.6.0')

    while True:
        host = q.get()
        vars   = snmp(vars, action='get', timeout=0.5, community='c0mcab113', peer=host)
        for var in vars:
            print("%s-%03d %s = %s: %s" % (host, i, var.oid, var.type, var.response))
        q.task_done()

host_list = ['xfwars-po-01']*int(sys.argv[1])
#host_list.append('10.255.255.254')

q = Queue()

#for i in range(len(host_list)):
for i in range(int(sys.argv[2])):
    worker = threading.Thread(target=worker_loop, args=(i+1, q), daemon=True)
    worker.start()
print("workers spawned:", threading.active_count()-1)

start = time.perf_counter()

[q.put(host) for host in host_list]

q.join()

print("%02fms" % ((time.perf_counter()-start)*1000))
