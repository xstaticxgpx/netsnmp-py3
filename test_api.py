#!/usr/bin/env python3

from netsnmp import *
from netsnmp._api import SNMPError
import sys, time

if __name__ == '__main__':
    oids      = ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0']
    vars      = SNMPVarlist()
    [vars.append(SNMPVarbind(oid)) for oid in oids]
    ips = ['archt01', 'archt02', 'archt03', 'archt04', 'archt05']
#    ips = ['archt06']

    start = time.perf_counter()
    print('SNMP GET on %s' % oids)
    for host in ips:

        try:
            ss, vars = snmp(None, vars, action='get', community='public', peer=host)
            for var in vars:
                print("%s = %s: %s" % (var.oid, var.type, var.response))
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
                print("%s = %s: %s" % (var.oid, var.type, var.response))
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
            print("%s = %s: %s" % (var.oid, var.type, var.response))
        ss.close()
    except SNMPError as e:
        print("%s = ERROR: %s" % (sys.argv[1], str(e).strip()))

    print("%02fms" % ((time.perf_counter()-start)*1000))
