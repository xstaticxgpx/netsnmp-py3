#!/usr/bin/env python3

#import netsnmp._api as netsnmp
from . import _api as netsnmp

class SNMPRuntimeError(netsnmp.SNMPError):
    pass

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

# Response tuple pointers
OID=0
TYPE=1
VALUE=2

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

    def __str__(self):
        return self.oid

class SNMPResponse(object):
    def __init__(self):
        self.response = None
        self.typestr = None
        self.oid = None

    def __str__(self):
        return self.oid

def snmp_compare_oid(oid1, oid2):
    """
    Return True if oid2 outside of oid1 tree
    Used by SNMPSession.walk
    """
    oid1_split = []
    [oid1_split.append(i) for i in oid1.split('.') if i]
    oid1_len = len(oid1_split)
    oid1_idx = oid1_len-1

    oid2_split = []
    [oid2_split.append(i) for i in oid2.split('.') if i]

    if oid2_split[oid1_idx] > oid1_split[-1]:
        return True
    return False

class SNMPSession(object):
    """
    Session based, thread-safe interface
    """
    def __init__(self, peername, community, version=SNMP_VER['2c'], timeout=0.5, retries=1, debug=0):
        self.debug     = debug # 1 for partial debugging, 2 for full NETSNMP debugging
        self.version   = version
        self.timeout   = int(timeout*1000000)
        self.retries   = retries
        self.community = community
        self.peername  = peername
        # Define session
        self.sess_ptr  = netsnmp.create_session(self.version, self.timeout, self.retries, 
                                                self.community, self.peername, self.debug)
        self.alive     = True

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
        if netsnmp.close_session(self):
            self.alive = False

    def get(self, oids):
        # Define list to be populated by C API get()
        responses = []
        # netsnmp.get(SNMPSession(), oids=[oid,..], responses=[])
        # Response information is appended as a tuple of (OID, TYPE, VALUE) to responses
        # Return 1 on success, possibly raises SNMPError() exception
        rc = netsnmp.get(self, oids, responses)
        # Sanity check rc
        if not rc:
            raise SNMPRuntimeError("Invalid return code", rc)
        return responses

    def getnext(self, oids):
        responses = []
        rc = netsnmp.getnext(self, oids, responses)
        if not rc:
            raise SNMPRuntimeError("Invalid return code", rc)
        return responses

    def walk(self, oids):
        for oid in oids:
            next_oid = oid
            while True:
                response = self.getnext([next_oid,])[0]
                if snmp_compare_oid(oid, response[OID]):
                    break
                next_oid = response[OID]
                yield response
        raise StopIteration

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
