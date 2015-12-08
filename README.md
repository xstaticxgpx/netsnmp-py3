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
creating build
creating build/temp.linux-x86_64-3.4
creating build/temp.linux-x86_64-3.4/netsnmp
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/session.c -o build/temp.linux-x86_64-3.4/netsnmp/session.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/get.c -o build/temp.linux-x86_64-3.4/netsnmp/get.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/getnext.c -o build/temp.linux-x86_64-3.4/netsnmp/getnext.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/get_async.c -o build/temp.linux-x86_64-3.4/netsnmp/get_async.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/interface.c -o build/temp.linux-x86_64-3.4/netsnmp/interface.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/_api.c -o build/temp.linux-x86_64-3.4/netsnmp/_api.o
creating build/lib.linux-x86_64-3.4
creating build/lib.linux-x86_64-3.4/netsnmp
x86_64-linux-gnu-gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,relro -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 build/temp.linux-x86_64-3.4/netsnmp/session.o build/temp.linux-x86_64-3.4/netsnmp/get.o build/temp.linux-x86_64-3.4/netsnmp/getnext.o build/temp.linux-x86_64-3.4/netsnmp/get_async.o build/temp.linux-x86_64-3.4/netsnmp/interface.o build/temp.linux-x86_64-3.4/netsnmp/_api.o -L/Build/net-snmp-5.7.3/agent/.libs -L/Build/net-snmp-5.7.3/snmplib/.libs -lnetsnmp -lcrypto -lm -lzmq -lczmq -o build/lib.linux-x86_64-3.4/netsnmp/_api.cpython-34m.so
copying build/lib.linux-x86_64-3.4/netsnmp/_api.cpython-34m.so -> netsnmp

$ ldd netsnmp/_api.cpython-34m.so 
    linux-vdso.so.1 (0x00007ffe9054d000)
    libnetsnmp.so.30 => /Build/net-snmp-5.7.3/snmplib/.libs/libnetsnmp.so.30 (0x00007fee1fd58000)
    libcrypto.so.1.0.2 => /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.2 (0x00007fee1f8f6000)
    libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007fee1f5f4000)
    libzmq.so.3 => /usr/lib/x86_64-linux-gnu/libzmq.so.3 (0x00007fee1f394000)
    libczmq.so.3 => /usr/lib/x86_64-linux-gnu/libczmq.so.3 (0x00007fee1f0eb000)
    libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fee1eecd000)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fee1eb24000)
    libcrypto.so.1.0.0 => /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.0 (0x00007fee1e6c3000)
    libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fee1e4be000)
    libpgm-5.1.so.0 => /usr/lib/libpgm-5.1.so.0 (0x00007fee1e271000)
    libsodium.so.13 => /usr/lib/x86_64-linux-gnu/libsodium.so.13 (0x00007fee1e01d000)
    librt.so.1 => /lib/x86_64-linux-gnu/librt.so.1 (0x00007fee1de14000)
    libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007fee1da99000)
    libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007fee1d883000)
    /lib64/ld-linux-x86-64.so.2 (0x000056369d47c000)
```



Test netsnmp-py3 functionality:

```
$ ./test_api.py
SNMP GET on ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0']
### created session at 0x27fc170
[archt01] received 3 responses in 0.467210ms
[archt01] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt01] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.54
[archt01] .1.3.6.1.2.1.1.5.0 = STRING: "archt01"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt02] received 3 responses in 0.252958ms
[archt02] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt02 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt02] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.40
[archt02] .1.3.6.1.2.1.1.5.0 = STRING: "archt02"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt03] received 3 responses in 0.282452ms
[archt03] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt03 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt03] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.38
[archt03] .1.3.6.1.2.1.1.5.0 = STRING: "archt03"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt04] received 3 responses in 0.233101ms
[archt04] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt04 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt04] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.12
[archt04] .1.3.6.1.2.1.1.5.0 = STRING: "archt04"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt05] received 3 responses in 0.212654ms
[archt05] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt05 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt05] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.14
[archt05] .1.3.6.1.2.1.1.5.0 = STRING: "archt05"
### closing session at 0x27fc170
Total time taken: 3.117ms

SNMP GETNEXT on ['.1.3.6.1.2.1.1.1', '.1.3.6.1.2.1.1.2.0', '.1.3.6.1.2.1.1.4.0']
### created session at 0x27fc170
[archt01] received 3 responses in 0.216976ms
[archt01] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt01] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.54
[archt01] .1.3.6.1.2.1.1.5.0 = STRING: "archt01"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt02] received 3 responses in 0.215313ms
[archt02] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt02 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt02] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.40
[archt02] .1.3.6.1.2.1.1.5.0 = STRING: "archt02"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt03] received 3 responses in 0.180036ms
[archt03] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt03 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt03] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.38
[archt03] .1.3.6.1.2.1.1.5.0 = STRING: "archt03"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt04] received 3 responses in 0.170726ms
[archt04] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt04 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt04] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.12
[archt04] .1.3.6.1.2.1.1.5.0 = STRING: "archt04"
### closing session at 0x27fc170
### created session at 0x27fc170
[archt05] received 3 responses in 0.160724ms
[archt05] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt05 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt05] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.14
[archt05] .1.3.6.1.2.1.1.5.0 = STRING: "archt05"
### closing session at 0x27fc170
Total time taken: 2.022ms

SNMP WALK on ['.1.3.6.1.2.1.1', '.1.3.6.1.4.1.2021.100']
### created session at 0x27fc170
[archt01] .1.3.6.1.2.1.1.1.0 = STRING: "Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"
[archt01] .1.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
[archt01] .1.3.6.1.2.1.1.3.0 = Timeticks: 1:8:43:39.54
[archt01] .1.3.6.1.2.1.1.4.0 = STRING: "root@localhost"
[archt01] .1.3.6.1.2.1.1.5.0 = STRING: "archt01"
[archt01] .1.3.6.1.2.1.1.6.0 = STRING: "Unknown"
[archt01] .1.3.6.1.2.1.1.8.0 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.2.1 = OID: iso.3.6.1.2.1.10.131
[archt01] .1.3.6.1.2.1.1.9.1.2.2 = OID: iso.3.6.1.6.3.11.3.1.1
[archt01] .1.3.6.1.2.1.1.9.1.2.3 = OID: iso.3.6.1.6.3.15.2.1.1
[archt01] .1.3.6.1.2.1.1.9.1.2.4 = OID: iso.3.6.1.6.3.10.3.1.1
[archt01] .1.3.6.1.2.1.1.9.1.2.5 = OID: iso.3.6.1.6.3.1
[archt01] .1.3.6.1.2.1.1.9.1.2.6 = OID: iso.3.6.1.6.3.16.2.2.1
[archt01] .1.3.6.1.2.1.1.9.1.2.7 = OID: iso.3.6.1.2.1.49
[archt01] .1.3.6.1.2.1.1.9.1.2.8 = OID: iso.3.6.1.2.1.4
[archt01] .1.3.6.1.2.1.1.9.1.2.9 = OID: iso.3.6.1.2.1.50
[archt01] .1.3.6.1.2.1.1.9.1.2.10 = OID: iso.3.6.1.6.3.13.3.1.3
[archt01] .1.3.6.1.2.1.1.9.1.2.11 = OID: iso.3.6.1.2.1.92
[archt01] .1.3.6.1.2.1.1.9.1.3.1 = STRING: "RFC 2667 TUNNEL-MIB implementation for Linux 2.2.x kernels."
[archt01] .1.3.6.1.2.1.1.9.1.3.2 = STRING: "The MIB for Message Processing and Dispatching."
[archt01] .1.3.6.1.2.1.1.9.1.3.3 = STRING: "The management information definitions for the SNMP User-based Security Model."
[archt01] .1.3.6.1.2.1.1.9.1.3.4 = STRING: "The SNMP Management Architecture MIB."
[archt01] .1.3.6.1.2.1.1.9.1.3.5 = STRING: "The MIB module for SNMPv2 entities"
[archt01] .1.3.6.1.2.1.1.9.1.3.6 = STRING: "View-based Access Control Model for SNMP."
[archt01] .1.3.6.1.2.1.1.9.1.3.7 = STRING: "The MIB module for managing TCP implementations"
[archt01] .1.3.6.1.2.1.1.9.1.3.8 = STRING: "The MIB module for managing IP and ICMP implementations"
[archt01] .1.3.6.1.2.1.1.9.1.3.9 = STRING: "The MIB module for managing UDP implementations"
[archt01] .1.3.6.1.2.1.1.9.1.3.10 = STRING: "The MIB modules for managing SNMP Notification, plus filtering."
[archt01] .1.3.6.1.2.1.1.9.1.3.11 = STRING: "The MIB module for logging SNMP Notifications."
[archt01] .1.3.6.1.2.1.1.9.1.4.1 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.2 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.3 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.4 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.5 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.6 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.7 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.8 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.9 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.10 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.2.1.1.9.1.4.11 = Timeticks: 0:0:00:00.00
[archt01] .1.3.6.1.4.1.2021.100.1.0 = INTEGER: 1
[archt01] .1.3.6.1.4.1.2021.100.2.0 = STRING: "5.7.3"
[archt01] .1.3.6.1.4.1.2021.100.3.0 = STRING: "$Date$"
[archt01] .1.3.6.1.4.1.2021.100.4.0 = STRING: "Tue Dec  8 00:24:21 2015"
[archt01] .1.3.6.1.4.1.2021.100.5.0 = STRING: "$Id$"
[archt01] .1.3.6.1.4.1.2021.100.6.0 = STRING: " '--prefix=/usr' '--sysconfdir=/etc' '--sbindir=/usr/bin' '--mandir=/usr/share/man' '--enable-ucd-snmp-compatibility' '--enable-ipv6' '--with-python-modules' '--with-default-snmp-version=3' '--with-sys-contact=root@localhost' '--with-sys-location=Unknown' '--with-logfile=/var/log/snmpd.log' '--with-mib-modules=host misc/ipfwacc ucd-snmp/diskio tunnel ucd-snmp/dlmod' '--with-persistent-directory=/var/net-snmp' 'CFLAGS=-march=x86-64 -mtune=generic -O2 -pipe -fstack-protector-strong --param=ssp-buffer-size=4' 'LDFLAGS=-Wl,-O1,--sort-common,--as-needed,-z,relro' 'CPPFLAGS=-D_FORTIFY_SOURCE=2'"
[archt01] .1.3.6.1.4.1.2021.100.10.0 = INTEGER: 0
[archt01] .1.3.6.1.4.1.2021.100.11.0 = INTEGER: 0
[archt01] .1.3.6.1.4.1.2021.100.12.0 = INTEGER: 0
[archt01] .1.3.6.1.4.1.2021.100.13.0 = INTEGER: 0
[archt01] .1.3.6.1.4.1.2021.100.20.0 = INTEGER: 0
### closing session at 0x27fc170
Total time taken: 17.839ms
```
