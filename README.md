# netsnmp-py3
Python3 NET-SNMP Bindings (C Extension)

Example usage: `python3 setup.py build_ext -i && ./test_api.py`

Currently only supports get, getnext, and walk for now

# Overview

Recommended to build this against a manually compiled NET-SNMP source - no need to install:

```
$ pwd
/Build/net-snmp-5.7.3

$ ./configure --prefix=/opt --enable-ucd-snmp-compatibility --enable-ipv6 --with-defaults
..
$ make
..
```

Build extension and check LDD for library linking, configure ld.so.conf if nescessary:
```
$ python3 setup.py --basedir=/Build/net-snmp-5.7.3 build_ext -i
running build_ext
building 'netsnmp._api' extension
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/session.c -o build/temp.linux-x86_64-3.4/netsnmp/session.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/get.c -o build/temp.linux-x86_64-3.4/netsnmp/get.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/getnext.c -o build/temp.linux-x86_64-3.4/netsnmp/getnext.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/walk.c -o build/temp.linux-x86_64-3.4/netsnmp/walk.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/extra.c -o build/temp.linux-x86_64-3.4/netsnmp/extra.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/_api.c -o build/temp.linux-x86_64-3.4/netsnmp/_api.o
x86_64-linux-gnu-gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,relro -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 build/temp.linux-x86_64-3.4/netsnmp/session.o build/temp.linux-x86_64-3.4/netsnmp/get.o build/temp.linux-x86_64-3.4/netsnmp/getnext.o build/temp.linux-x86_64-3.4/netsnmp/walk.o build/temp.linux-x86_64-3.4/netsnmp/extra.o build/temp.linux-x86_64-3.4/netsnmp/_api.o -L/Build/net-snmp-5.7.3/agent/.libs -L/Build/net-snmp-5.7.3/snmplib/.libs -lnetsnmp -lcrypto -lm -o build/lib.linux-x86_64-3.4/netsnmp/_api.cpython-34m.so
copying build/lib.linux-x86_64-3.4/netsnmp/_api.cpython-34m.so -> netsnmp

$ ldd netsnmp/_api.cpython-34m.so 
    linux-vdso.so.1 (0x00007ffcdc1f5000)
    libnetsnmp.so.30 => /Build/net-snmp-5.7.3/snmplib/.libs/libnetsnmp.so.30 (0x00007f9eca7cf000)
    libcrypto.so.1.0.0 => /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0 (0x00007f9eca3d4000)
    libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f9eca0d2000)
    libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f9ec9eb5000)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f9ec9b0c000)
    libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f9ec9907000)
    /lib64/ld-linux-x86-64.so.2 (0x000055e727849000)
```



Test netsnmp-py3 functionality:

```
$ ./test_api.py
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
