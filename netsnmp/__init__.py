#!/usr/bin/env python3

import netsnmp._api as netsnmp

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
        self.typestr  = None
        self.oid      = None

class SNMPSession():
    def __init__(self, version=SNMP_VER['2c'], timeout=0.5, retries=1, community=None, peername=None):
        self.debug     = 0
        self.version   = version
        self.timeout   = int(timeout*1000000)
        self.retries   = retries
        self.community = community
        self.peername  = peername
        self.sess_ptr  = netsnmp.create_session(self.version, self.timeout, self.retries, 
                                                self.community, self.peername, self.debug)

    def nullvar(self):
        """
        Called in C API walk function, returns new SNMPVarbind object reference
        """
        return SNMPVarbind()

    def close(self):
        res = netsnmp.close_session(self)

    def get(self, varlist):
        res = netsnmp.get(self, varlist)
        return res

    def getnext(self, varlist):
        res = netsnmp.getnext(self, varlist)
        return res

    def walk(self, varlist):
        res = netsnmp.walk(self, varlist)
        return res

def snmp(session, var, action='get', timeout=0.5, community=None, peer=None):
    if not session:
        session = SNMPSession(community=community, peername=peer)

    if isinstance(var, SNMPVarlist):
        vars = var
    elif not isinstance(var, SNMPVarbind):
        vars = SNMPVarlist()
        vars.append(SNMPVarbind(var))

    if action == 'get':
        ret = session.get(vars)
    elif action == 'getnext':
        ret = session.getnext(vars)
    elif action == 'walk':
        ret = session.walk(vars)

    return (session, vars)
