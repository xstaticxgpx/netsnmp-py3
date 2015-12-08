#!/usr/bin/env python3

from netsnmp import *
from netsnmp._api import SNMPError
import sys, time

if __name__ == '__main__':
    ips = ['archt01', 'archt02', 'archt03', 'archt04', 'archt05']
    ips6 = ['udp6:[fe80::c67:bb2b:dbb4:8c63]', 'udp6:[fe80::ce0b:fd3a:ac06:26a9]', 'udp6:[fe80::b97d:dda5:1b0e:dd2e]', 'udp6:[fe80::44ee:1be2:784b:84ed]', 'udp6:[fe80::ba63:79c3:cfdd:599d]']


    try:
        sys.argv[1]
    except IndexError:
        [sys.argv.append(op) for op in ('get', 'getnext', 'walk')]

    if 'get' in sys.argv[1:]:
        oids      = ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0']
        start = time.perf_counter()
        print('SNMP GET on %s' % oids)
        for host in ips:
            try:
                _start = time.perf_counter()
                # Context (automatically closes session)
                with SNMPSession(host, 'public', debug=1) as ss:
                    responses = ss.get(oids)
                    print('[%s] received %d responses in %02fms' % (host, len(responses), (time.perf_counter()-_start)*1000))
                    [print("[%s] %s = %s: %s" % (host, oid[OID], oid[TYPE], oid[VALUE])) for oid in responses]
    
                # Non-context
                #ss = SNMPSession(host, 'public', debug=1)
                #responses = ss.get(oids)
                #print('[%s] received %d responses in %02fms' % (host, len(responses), (time.perf_counter()-_start)*1000))
                #[print("[%s] %s = %s: %s" % (host, oid[OID], oid[TYPE], oid[VALUE])) for oid in responses]
                #ss.close()
    
            except SNMPError as e:
                # This would ensure session is closed incase context was not used
                try:
                    if ss.alive:
                        ss.close()
                except:
                    pass
    
                print("[%s]" % host, repr(e))
                continue
    
        print("Total time taken: %.03fms" % ((time.perf_counter()-start)*1000))
        print()

    if 'getnext' in sys.argv[1:]:
        oids      = ['.1.3.6.1.2.1.1.1', '.1.3.6.1.2.1.1.2.0', '.1.3.6.1.2.1.1.4.0']
        start = time.perf_counter()
        print('SNMP GETNEXT on %s' % oids)
        for host in ips:
            try:
                _start = time.perf_counter()
                with SNMPSession(host, 'public', debug=1) as ss:
                    responses = ss.getnext(oids)
                    print('[%s] received %d responses in %02fms' % (host, len(responses), (time.perf_counter()-_start)*1000))
                    [print("[%s] %s = %s: %s" % (host, oid[OID], oid[TYPE], oid[VALUE])) for oid in responses]
    
            except SNMPError as e:
                try:
                    if ss.alive:
                        ss.close()
                except:
                    pass
    
                print("[%s]" % host, repr(e))
                continue
    
        print("Total time taken: %.03fms" % ((time.perf_counter()-start)*1000))
        print()

    if 'walk' in sys.argv[1:]:
        oids = ['.1.3.6.1.2.1.1', '.1.3.6.1.4.1.2021.100']
        start = time.perf_counter()
        print('SNMP WALK on %s' % oids)
        for host in ips[:1]:
            try:
                _start = time.perf_counter()
                with SNMPSession(host, 'public', debug=1) as ss:
                    # SNMPSession.walk is a generator
                    [print("[%s] %s = %s: %s" % (host, response[OID], response[TYPE], response[VALUE])) for response in ss.walk(oids)]
    
            except SNMPError as e:
                try:
                    if ss.alive:
                        ss.close()
                except:
                    pass
    
                print("[%s]" % host, repr(e))
                continue
    
        print("Total time taken: %.03fms" % ((time.perf_counter()-start)*1000))
        print()
