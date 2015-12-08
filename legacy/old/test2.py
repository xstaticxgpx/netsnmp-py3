#!/usr/bin/env python3

import netsnmp.client_intf as netsnmp

args = {
        "version": 2,
        "community": 'c0mcab113',
        "peer": 'localhost',
        "lport": 0,
        "retries": 1,
        "timeout": 10000,
        }

ret = netsnmp.test(2, 'c0mcab113', 'localhost')
print(ret)
#varbind = netsnmp.Varbind("IF-MIB::ifIndex")
#netsnmp.Varbind.print_str(varbind)
#netsnmp.snmpwalk('IF-MIB::ifIndex', **args)
#test = netsnmp.netsnmp_get(varbind, **args)

#for idx in netsnmp.snmpwalk(netsnmp.Varbind("IF-MIB::ifIndex"),
#                            **args):
#    descr, oper, cin, cout = netsnmp.snmpget(
#            netsnmp.Varbind("IF-MIB::ifDescr", idx),
#            netsnmp.Varbind("IF-MIB::ifOperStatus", idx),
#            netsnmp.Varbind("IF-MIB::ifInOctets", idx),
#            netsnmp.Varbind("IF-MIB::ifOutOctets", idx),
#            **args)
#    print(idx)
#    assert(descr is not None and
#           cin is not None and
#           cout is not None)
#    if descr == "lo":
#        continue
#    if oper != "1":
#        continue
#    print("{} {} {}".format(descr, cin, cout))
