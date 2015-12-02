#!/usr/bin/env python3

import sys
import test_api
import threading
import time
import subprocess
from queue import Queue


def worker_loop(i, q):

    #vars      = '.1.3.6.1.2.1.1.1.0'
    vars      = '.1.3.6.1.2.1.1.1.0 .1.3.6.1.2.1.1.3.0 .1.3.6.1.2.1.1.5.0 .1.3.6.1.2.1.1.6.0'

    while True:
        host = q.get()
        output = subprocess.check_output("%s %s -c %s -t %s %s %s" %
                        ("snmpget", "-v2c -M/dev/null", "c0mcab113", 5, host, vars),
                        shell=True,
                        stderr=subprocess.DEVNULL)
        print(i, output)
        q.task_done()

host_list = ['xfwars-po-01']*int(sys.argv[1])

q = Queue()

for i in range(int(sys.argv[2])):
#for i in range(50):
    worker = threading.Thread(target=worker_loop, args=(i+1, q), daemon=True)
    worker.start()
print("workers spawned:", threading.active_count()-1)

start = time.perf_counter()

[q.put(host) for host in host_list]

q.join()

print("%02fms" % ((time.perf_counter()-start)*1000))
