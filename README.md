# netsnmp-py3
[![Build Status](https://travis-ci.org/xstaticxgpx/netsnmp-py3.svg?branch=master)](https://travis-ci.org/xstaticxgpx/netsnmp-py3)

Python NET-SNMP Bindings (C Extension)

https://pypi.python.org/pypi/netsnmp-py

Supports Python 2.7 and 3.x


Currently only supports SNMPv1 and SNMPv2c polling (GET, GETNEXT, WALK)

Support for SET and TRAP, as well as SNMPv3 is planned

# Overview

### Pip Install

##### Debian testing/unstable (py2.7)
```
# apt-get install libsnmp30 libsnmp30-dev python-zmq libczmq3 libczmq-dev
# pip install netsnmp-py
```

##### Debian testing/unstable (py3)
```
# apt-get install libsnmp30 libsnmp30-dev libczmq3 libczmq-dev
# pip3 install pyzmq
# pip3 install netsnmp-py
```

### Manual Setup

Recommended to build this against a manually compiled NET-SNMP source - no need to install:

```
$ pwd
/Build/net-snmp-5.7.3

$ ./configure --prefix=/opt --enable-ucd-snmp-compatibility --enable-ipv6 --with-defaults
..
$ make
..
```

Build the netsnmp C extension and check LDD for proper library linking, configure ld.so.conf if nescessary:
```
$ python3 setup.py --basedir=/Build/net-snmp-5.7.3 build_ext -i
running build_ext
building 'netsnmp._api' extension
creating build
creating build/temp.linux-x86_64-3.4
creating build/temp.linux-x86_64-3.4/netsnmp
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/session.c -o build/temp.linux-x86_64-3.4/netsnmp/session.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/get.c -o build/temp.linux-x86_64-3.4/netsnmp/get.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/get_async.c -o build/temp.linux-x86_64-3.4/netsnmp/get_async.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/interface.c -o build/temp.linux-x86_64-3.4/netsnmp/interface.o
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 -fPIC -I/Build/net-snmp-5.7.3/include -I./netsnmp -I/usr/include/python3.4m -c netsnmp/_api.c -o build/temp.linux-x86_64-3.4/netsnmp/_api.o
creating build/lib.linux-x86_64-3.4
creating build/lib.linux-x86_64-3.4/netsnmp
x86_64-linux-gnu-gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,relro -g -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2 build/temp.linux-x86_64-3.4/netsnmp/session.o build/temp.linux-x86_64-3.4/netsnmp/get.o build/temp.linux-x86_64-3.4/netsnmp/get_async.o build/temp.linux-x86_64-3.4/netsnmp/interface.o build/temp.linux-x86_64-3.4/netsnmp/_api.o -L/Build/net-snmp-5.7.3/agent/.libs -L/Build/net-snmp-5.7.3/snmplib/.libs -lnetsnmp -lcrypto -lm -lzmq -lczmq -o build/lib.linux-x86_64-3.4/netsnmp/_api.cpython-34m.so
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

### Basic usage:

SNMP GET:
```
>>> with netsnmp.SNMPSession('archt01', 'public') as ss:
...     ss.get(['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0'])
... 
[('.1.3.6.1.2.1.1.1.0', 'STRING', '"Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"'), ('.1.3.6.1.2.1.1.3.0', 'Timeticks', '1:11:36:30.56'), ('.1.3.6.1.2.1.1.5.0', 'STRING', '"archt01"')]
```

SNMP GETNEXT:
```
>>> with netsnmp.SNMPSession('archt01', 'public') as ss:
...     ss.getnext(['.1.3.6.1.2.1.1.1', '.1.3.6.1.2.1.1.2.0', '.1.3.6.1.2.1.1.4.0'])
... 
[('.1.3.6.1.2.1.1.1.0', 'STRING', '"Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"'), ('.1.3.6.1.2.1.1.3.0', 'Timeticks', '1:11:39:35.05'), ('.1.3.6.1.2.1.1.5.0', 'STRING', '"archt01"')]
```

SNMP WALK (generator):
```
>>> with netsnmp.SNMPSession('archt01', 'public') as ss:
...     [response for response in ss.walk(['.1.3.6.1.4.1.2021.10.1.3'])]
... 
[('.1.3.6.1.4.1.2021.10.1.3.1', 'STRING', '"0.37"'), ('.1.3.6.1.4.1.2021.10.1.3.2', 'STRING', '"0.25"'), ('.1.3.6.1.4.1.2021.10.1.3.3', 'STRING', '"0.29"')]
```

IPv6 support:
```
>>> with netsnmp.SNMPSession('udp6:[fe80::c67:bb2b:dbb4:8c63]', 'public') as ss:
...     ss.get(['.1.3.6.1.2.1.1.1.0'])
... 
[('.1.3.6.1.2.1.1.1.0', 'STRING', '"Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"')]
```
