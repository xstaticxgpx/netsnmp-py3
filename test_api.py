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
        oids = ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0', '.1.3.6.1.2.1.55.1.5.1.8.2', '.1.3.6.1.2.1.25.1.2.0']
        #oids = [oids.pop(),]
        start = time.perf_counter()
        print('SNMP GET on %s' % oids)
        for host in ips:
            try:
                _start = time.perf_counter()
                # Context (automatically closes session)
                with SNMPSession(host, 'public', debug=1) as ss:
                    responses = ss.get(oids)
                    print('[%s] received %d responses in %02fms' % (host, len(responses), (time.perf_counter()-_start)*1000))
                    # example including conversion of hex-string:
                    for oid in responses:
                        _type, _value = snmp_hex2str(oid[TYPE], oid[VALUE]) if oid[TYPE]=="Hex-STRING" else (oid[TYPE], oid[VALUE])
                        print("[%s] %s = %s: %s" % (host, oid[OID], _type, _value))
                    #    if oid[OID] == ".1.3.6.1.2.1.25.1.2.0" or oid[OID] == ".1.3.6.1.2.1.55.1.5.1.8.2":
                    #        print("HEX2STR func:", snmp_hex2str(oid[VALUE]))
                             #for char in b'07 DF 0C 0E 04 1D 11 00 2D 05 00 '.split(): ord(binascii.unhexlify(char))
                             #year1, year2, month, day, hour, minute, second, _, _, _, _   = [ord(binascii.unhexlify(char)) for char in oid[VALUE].replace('"', '').split()]



    
                # Non-context
                #ss = SNMPSession(host, 'public', debug=1)
                #responses = ss.get(oids)
                #print('[%s] received %d responses in %02fms' % (host, len(responses), (time.perf_counter()-_start)*1000))
                #[print("[%s] %s = %s: %s" % (host, oid[OID], oid[TYPE], oid[VALUE])) for oid in responses]
                #ss.close()
    
            except SNMPError as e:
                # This would ensure session is closed incase context was not used
                try:
                    if ss.is_alive():
                        ss.close()
                except:
                    pass
    
                print("[%s]" % host, repr(e))
                continue
    
        print("Total time taken: %.03fms" % ((time.perf_counter()-start)*1000))
        print()

    if 'getnext' in sys.argv[1:]:
        oids = ['.1.3.6.1.2.1.1', '.1.3.6.1.2.1.1.2.0', '.1.3.6.1.2.1.1.4.0']
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
                    if ss.is_alive():
                        ss.close()
                except:
                    pass
    
                print("[%s]" % host, repr(e))
                continue
    
        print("Total time taken: %.03fms" % ((time.perf_counter()-start)*1000))
        print()

    if 'walk' in sys.argv[1:]:
        oids = ['.1.3.6.1.2.1.1']
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
                    if ss.is_alive():
                        ss.close()
                except:
                    pass
    
                print("[%s]" % host, repr(e))
                continue
    
        print("Total time taken: %.03fms" % ((time.perf_counter()-start)*1000))
        print()
