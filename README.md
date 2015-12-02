# netsnmp-py3
Python3 NET-SNMP Bindings (C Extension)

Example usage: `python3 setup.py build_ext -i && ./test_api.py .1.3.6.1.2.1.1.1.0`

Currently only supports get, getnext, and walk for now

# Overview

Recommended to build this against a manually compiled NET-SNMP source - no need to install:

```
$ pwd
/Build/net-snmp-5.7.3

$ ./configure --prefix=/opt --enable-minimalist --enable-ipv6 --with-defaults
..
$ make
..
```

Test netsnmp-py3 functionality:

```
$ python3 setup.py --basedir=/Build/net-snmp-5.7.3 build_ext -i && ./test_api.py .1.3.6.1.2.1.1.1.0
running build_ext
copying build/lib.linux-x86_64-3.4/netsnmp/api.cpython-34m.so -> netsnmp
SNMP GET on ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0']
.1.3.6.1.2.1.1.1.0 = STRING: "Linux archt01 4.1.12-1-ck #1 SMP PREEMPT Tue Oct 27 18:04:34 EDT 2015 x86_64"
.1.3.6.1.2.1.1.3.0 = Timeticks: 0:0:11:50.48
.1.3.6.1.2.1.1.5.0 = STRING: "archt01"
0.531936ms
SNMP GETNEXT on ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0']
.1.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
.1.3.6.1.2.1.1.4.0 = STRING: "root@localhost"
.1.3.6.1.2.1.1.6.0 = STRING: "Unknown"
0.305908ms
SNMP WALK on ['.1.3.6.1.2.1.1', '1.3.6.1.2.1.2']
.1.3.6.1.2.1.1.1.0 = STRING: "Linux archt01 4.1.12-1-ck #1 SMP PREEMPT Tue Oct 27 18:04:34 EDT 2015 x86_64"
.1.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
.1.3.6.1.2.1.1.3.0 = Timeticks: 0:0:11:50.48
.1.3.6.1.2.1.1.4.0 = STRING: "root@localhost"
.1.3.6.1.2.1.1.5.0 = STRING: "archt01"
.1.3.6.1.2.1.1.6.0 = STRING: "Unknown"
.1.3.6.1.2.1.1.8.0 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.2.1 = OID: iso.3.6.1.2.1.10.131
.1.3.6.1.2.1.1.9.1.2.2 = OID: iso.3.6.1.6.3.11.3.1.1
.1.3.6.1.2.1.1.9.1.2.3 = OID: iso.3.6.1.6.3.15.2.1.1
.1.3.6.1.2.1.1.9.1.2.4 = OID: iso.3.6.1.6.3.10.3.1.1
.1.3.6.1.2.1.1.9.1.2.5 = OID: iso.3.6.1.6.3.1
.1.3.6.1.2.1.1.9.1.2.6 = OID: iso.3.6.1.6.3.16.2.2.1
.1.3.6.1.2.1.1.9.1.2.7 = OID: iso.3.6.1.2.1.49
.1.3.6.1.2.1.1.9.1.2.8 = OID: iso.3.6.1.2.1.4
.1.3.6.1.2.1.1.9.1.2.9 = OID: iso.3.6.1.2.1.50
.1.3.6.1.2.1.1.9.1.2.10 = OID: iso.3.6.1.6.3.13.3.1.3
.1.3.6.1.2.1.1.9.1.2.11 = OID: iso.3.6.1.2.1.92
.1.3.6.1.2.1.1.9.1.3.1 = STRING: "RFC 2667 TUNNEL-MIB implementation for Linux 2.2.x kernels."
.1.3.6.1.2.1.1.9.1.3.2 = STRING: "The MIB for Message Processing and Dispatching."
.1.3.6.1.2.1.1.9.1.3.3 = STRING: "The management information definitions for the SNMP User-based Security Model."
.1.3.6.1.2.1.1.9.1.3.4 = STRING: "The SNMP Management Architecture MIB."
.1.3.6.1.2.1.1.9.1.3.5 = STRING: "The MIB module for SNMPv2 entities"
.1.3.6.1.2.1.1.9.1.3.6 = STRING: "View-based Access Control Model for SNMP."
.1.3.6.1.2.1.1.9.1.3.8 = STRING: "The MIB module for managing IP and ICMP implementations"
.1.3.6.1.2.1.1.9.1.3.9 = STRING: "The MIB module for managing UDP implementations"
.1.3.6.1.2.1.1.9.1.3.10 = STRING: "The MIB modules for managing SNMP Notification, plus filtering."
.1.3.6.1.2.1.1.9.1.3.11 = STRING: "The MIB module for logging SNMP Notifications."
.1.3.6.1.2.1.1.9.1.4.1 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.2 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.3 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.4 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.5 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.6 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.7 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.8 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.9 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.10 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.1.9.1.4.11 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.2.1.0 = INTEGER: 2
.1.3.6.1.2.1.2.2.1.1.1 = INTEGER: 1
.1.3.6.1.2.1.2.2.1.1.2 = INTEGER: 2
.1.3.6.1.2.1.2.2.1.2.1 = STRING: "lo"
.1.3.6.1.2.1.2.2.1.2.2 = STRING: "host0"
.1.3.6.1.2.1.2.2.1.3.1 = INTEGER: 24
.1.3.6.1.2.1.2.2.1.3.2 = INTEGER: 6
.1.3.6.1.2.1.2.2.1.4.1 = INTEGER: 65536
.1.3.6.1.2.1.2.2.1.4.2 = INTEGER: 1500
.1.3.6.1.2.1.2.2.1.5.1 = Gauge32: 10000000
.1.3.6.1.2.1.2.2.1.5.2 = Gauge32: 4294967295
.1.3.6.1.2.1.2.2.1.6.1 = STRING: ""
.1.3.6.1.2.1.2.2.1.6.2 = STRING: "96 1F 3C 2E 62 36 "
.1.3.6.1.2.1.2.2.1.7.1 = INTEGER: 1
.1.3.6.1.2.1.2.2.1.7.2 = INTEGER: 1
.1.3.6.1.2.1.2.2.1.8.1 = INTEGER: 1
.1.3.6.1.2.1.2.2.1.8.2 = INTEGER: 1
.1.3.6.1.2.1.2.2.1.9.1 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.2.2.1.9.2 = Timeticks: 0:0:00:00.00
.1.3.6.1.2.1.2.2.1.10.1 = Counter32: 923215
.1.3.6.1.2.1.2.2.1.10.2 = Counter32: 194644605
.1.3.6.1.2.1.2.2.1.11.1 = Counter32: 10091
.1.3.6.1.2.1.2.2.1.11.2 = Counter32: 403189
.1.3.6.1.2.1.2.2.1.12.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.12.2 = Counter32: 0
.1.3.6.1.2.1.2.2.1.13.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.13.2 = Counter32: 103
.1.3.6.1.2.1.2.2.1.14.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.14.2 = Counter32: 0
.1.3.6.1.2.1.2.2.1.15.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.15.2 = Counter32: 0
.1.3.6.1.2.1.2.2.1.16.1 = Counter32: 923215
.1.3.6.1.2.1.2.2.1.16.2 = Counter32: 19770914
.1.3.6.1.2.1.2.2.1.17.1 = Counter32: 10091
.1.3.6.1.2.1.2.2.1.17.2 = Counter32: 128512
.1.3.6.1.2.1.2.2.1.18.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.18.2 = Counter32: 0
.1.3.6.1.2.1.2.2.1.19.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.19.2 = Counter32: 0
.1.3.6.1.2.1.2.2.1.20.1 = Counter32: 0
.1.3.6.1.2.1.2.2.1.20.2 = Counter32: 0
.1.3.6.1.2.1.2.2.1.21.1 = Gauge32: 0
.1.3.6.1.2.1.2.2.1.21.2 = Gauge32: 0
.1.3.6.1.2.1.2.2.1.22.1 = OID: ccitt.0
.1.3.6.1.2.1.2.2.1.22.2 = OID: ccitt.0
7.793924ms
```
