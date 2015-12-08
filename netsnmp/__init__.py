#!/usr/bin/env python3
"""
Docstring
"""

#import netsnmp._api as netsnmp
from . import _api as netsnmp

SNMPError = netsnmp.SNMPError

class SNMPRuntimeError(SNMPError): # pylint: disable=no-init
    """
    Raised by SNMPSession methods on return code error
    """
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
OID = 0
TYPE = 1
VALUE = 2

def snmp_compare_oid(oid1, oid2):
    """
    Return True if oid2 outside of oid1 tree
    Used by SNMPSession.walk
    """
    oid1_split = []
    [oid1_split.append(i) for i in oid1.split('.') if i] # pylint: disable=expression-not-assigned
    oid1_len = len(oid1_split)
    oid1_idx = oid1_len-1

    oid2_split = []
    [oid2_split.append(i) for i in oid2.split('.') if i] # pylint: disable=expression-not-assigned

    if oid2_split[oid1_idx] > oid1_split[oid1_idx]:
        return True
    return False

class SNMPSession(object):
    """
    Session based, thread-safe interface
    """
    def __init__(self, peername, community, version=SNMP_VER['2c'], timeout=0.5, retries=1, debug=0): # pylint: disable=line-too-long
        self.debug = debug # 1 for partial debugging, 2 for full NETSNMP debugging
        self.version = version
        self.timeout = int(timeout*1000000) # milliseconds converted to... microsec?
        self.retries = retries
        self.peername = peername
        self.community = community
        # Define session
        self.sess_ptr = netsnmp.create_session(self.version, self.timeout, self.retries,
                                               self.community, self.peername, self.debug)
        self.alive = True

    # Support context (with SNMPSession() as ss..)
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """
        Close session (clear file descriptors)
        """
        if netsnmp.close_session(self):
            self.alive = False

    def get(self, oids):
        """
        Wrap netsnmp._api.get C function
        """
        # Define list to be populated by C API get()
        responses = []
        # netsnmp.get(SNMPSession(), oids=[oid,..], responses=[])
        # Response information is appended as a tuple of (OID, TYPE, VALUE) to responses
        # Return 1 on success, possibly raises SNMPError() exception
        _rc = netsnmp.get(self, oids, responses)
        # Sanity check rc
        if not _rc:
            raise SNMPRuntimeError("Invalid return code", _rc)
        return responses

    def getnext(self, oids):
        """
        Wrap netsnmp._api.getnext C function
        """
        responses = []
        _rc = netsnmp.getnext(self, oids, responses)
        if not _rc:
            raise SNMPRuntimeError("Invalid return code", _rc)
        return responses

    def walk(self, oids):
        """
        Implement walk functionality by wrapping SNMPSession.getnext
        """
        for oid in oids:
            next_oid = oid
            while True:
                response = self.getnext([next_oid,])[0]
                if snmp_compare_oid(oid, response[OID]):
                    break
                next_oid = response[OID]
                yield response
        raise StopIteration
