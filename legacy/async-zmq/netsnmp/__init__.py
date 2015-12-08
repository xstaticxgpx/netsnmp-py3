#!/usr/bin/env python3

import asyncio
import random
import netsnmp.api as netsnmp

SNMP_VER = {
            '1': 0,
            '2c': 1,
            '3': 3,
}

SNMP_ERR = [
            'NOSUCHINSTANCE',
            'ENDOFMIBVIEW',
            'NOSUCHOBJECT',
            'ERROR',
]

class SNMPVarlist(list):
    pass

class SNMPVarbind(object):
    def __init__(self, request=None):
        # Request
        self.request  = request
        # Response attributes
        self.response = None
        self.type     = None
        self.oid      = None

class SNMPSession():
    def __init__(self, version=SNMP_VER['2c'], timeout=2, retries=0, community=None, peername=None):
        self.debug     = 1
        self.varlist   = None
        self.version   = version
        self.timeout   = int(timeout*1000000)
        self.retries   = retries
        self.community = community
        self.peername  = peername
        #self.sess_ptr  = netsnmp.create_session(self.version, self.timeout, self.retries, 
        #                                        self.community, self.peername, self.debug)

    def callback(self, reqid, peername, oid, type, response):
        print('%s received response on %s [%d] = %s: %s' % (peername, oid, reqid, type, response))
        return

    def nullvar(self):
        """
        Called in C API walk function, returns new SNMPVarbind object reference
        """
        return SNMPVarbind()

    def close(self):
        res = netsnmp.close_session(self)
        self.sess_ptr = None
        return

    def open(self):
        self.sess_ptr = netsnmp.create_session(self, self.version, self.timeout, self.retries, 
                                               self.community, self.peername, self.debug)

    @asyncio.coroutine
    def get(self, varlist):
        res = netsnmp.get(self, varlist)
        self.varlist=varlist
        yield

    @asyncio.coroutine
    def getnext(self, varlist):
        res = netsnmp.getnext(self, varlist)
        self.varlist=varlist
        return

    @asyncio.coroutine
    def walk(self, varlist):
        res = netsnmp.walk(self, varlist)
        self.varlist=varlist
        return res

@asyncio.coroutine
def snmp(session, var, action='get', timeout=0.5, community=None, peer=None, loop=None):
    if not session:
        session = SNMPSession(community=community, peername=peer)

    #if isinstance(var, SNMPVarlist):
    #    vars = var
    #elif not isinstance(var, SNMPVarbind):
    #    vars = SNMPVarlist()
    #    vars.append(SNMPVarbind(var))

    #if action == 'get':
    #    yield from session.get(vars)
    #elif action == 'getnext':
    #    yield from session.getnext(vars)
    #elif action == 'walk':
    #    yield from session.walk(vars)

    sleep = random.randint(1,9)/1000
    #yield from asyncio.sleep(sleep, loop=loop)
    #print('sleeping for %.3fms' % sleep)
    return netsnmp.get(session, vars)
