#!/usr/bin/env python3

#import netsnmp._api as netsnmp
from . import _api as netsnmp

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
    """
    Session based, thread-safe interface
    """
    def __init__(self, peername, community, version=SNMP_VER['2c'], timeout=0.5, retries=1):
        self.debug     = 0
        self.version   = version
        self.timeout   = int(timeout*1000000)
        self.retries   = retries
        self.community = community
        self.peername  = peername
        # Define session
        self.sess_ptr  = netsnmp.create_session(self.version, self.timeout, self.retries, 
                                                self.community, self.peername, self.debug)

    # Support context (with SNMPSession() as ss..)
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def nullvar(self):
        """
        Called in C API walk function, returns new SNMPVarbind object reference
        """
        return SNMPVarbind()

    def close(self):
        res = netsnmp.close_session(self)
        return res

    def get(self, oids):
        res = netsnmp.get(self, oids)
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
