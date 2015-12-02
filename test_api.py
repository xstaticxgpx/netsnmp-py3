#!/usr/bin/env python3

from netsnmp import *
from netsnmp._api import SNMPError
import sys, time

if __name__ == '__main__':
    oids      = ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0']
    vars      = SNMPVarlist()
    [vars.append(SNMPVarbind(oid)) for oid in oids]
    ips = ['archt01', 'archt02', 'archt03', 'archt04', 'archt05']
    ips6 = ['udp6:[fe80::c67:bb2b:dbb4:8c63]', 'udp6:[fe80::ce0b:fd3a:ac06:26a9]', 'udp6:[fe80::b97d:dda5:1b0e:dd2e]', 'udp6:[fe80::44ee:1be2:784b:84ed]', 'udp6:[fe80::ba63:79c3:cfdd:599d]']
    print(ips6)
    ips = ['archt01']

    start = time.perf_counter()
    print('SNMP GET on %s' % oids)
    for host in ips:

        try:
            ss, vars = snmp(None, vars, action='get', community='public', peer=host)
            for var in vars:
                print("%s = %s: %s" % (var.oid, var.typestr, var.response))
        except SNMPError as e:
            print("%s = ERROR: %s" % (vars[0].request, str(e).strip()))
            continue
        ss.close()

    print("%02fms" % ((time.perf_counter()-start)*1000))

    start = time.perf_counter()
    print('SNMP GETNEXT on %s' % oids)
    for host in ips:

        try:
            ss, vars = snmp(None, vars, action='getnext', community='public', peer=host)
            for var in vars:
                print("%s = %s: %s" % (var.oid, var.typestr, var.response))
        except SNMPError as e:
            print("%s = ERROR: %s" % (vars[0].request, str(e).strip()))
            continue
        ss.close()
    print("%02fms" % ((time.perf_counter()-start)*1000))


    start = time.perf_counter()
    oids = ['.1.3.6.1.2.1.1', '1.3.6.1.2.1.2']
    vars      = SNMPVarlist()
    [vars.append(SNMPVarbind(oid)) for oid in oids]
    print('SNMP WALK on %s' % oids)
    try:
        ss, vars = snmp(None, vars, action='walk', community='public', peer=ips[0])
        for var in vars:
            print("%s = %s: %s" % (var.oid, var.typestr, var.response))
        ss.close()
    except SNMPError as e:
        print("%s = ERROR: %s" % (sys.argv[1], str(e).strip()))

    print("%02fms" % ((time.perf_counter()-start)*1000))
