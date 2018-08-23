#!/usr/bin/env python3
"""
https://github.com/xstaticxgpx/netsnmp-py3/

Examples:

SNMP GET
---
    >>> with netsnmp.SNMPSession('archt01', 'public') as ss:
    ...     ss.get(['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.3.0', '.1.3.6.1.2.1.1.5.0'])
    ... 
    [('.1.3.6.1.2.1.1.1.0', 'STRING', '"Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"'), ('.1.3.6.1.2.1.1.3.0', 'Timeticks', '1:11:36:30.56'), ('.1.3.6.1.2.1.1.5.0', 'STRING', '"archt01"')]

SNMP GETNEXT
---
    >>> with netsnmp.SNMPSession('archt01', 'public') as ss:
    ...     ss.getnext(['.1.3.6.1.2.1.1.1', '.1.3.6.1.2.1.1.2.0', '.1.3.6.1.2.1.1.4.0'])
    ... 
    [('.1.3.6.1.2.1.1.1.0', 'STRING', '"Linux archt01 4.3.0-1-ck #1 SMP PREEMPT Sun Nov 15 13:24:29 EST 2015 x86_64"'), ('.1.3.6.1.2.1.1.3.0', 'Timeticks', '1:11:39:35.05'), ('.1.3.6.1.2.1.1.5.0', 'STRING', '"archt01"')]

SNMP WALK (load averages)
---
    >>> with netsnmp.SNMPSession('archt01', 'public') as ss:
    >>>     [response for response in ss.walk(['.1.3.6.1.4.1.2021.10.1.3'])]
    ... 
    [('.1.3.6.1.4.1.2021.10.1.3.1', 'STRING', '"0.37"'), ('.1.3.6.1.4.1.2021.10.1.3.2', 'STRING', '"0.25"'), ('.1.3.6.1.4.1.2021.10.1.3.3', 'STRING', '"0.29"')]

"""

#import netsnmp._api as netsnmp
from . import _api as netsnmp
from ._hex import snmp_hex2str

class SNMPRuntimeError(netsnmp.SNMPError): # pylint: disable=no-init
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

def oid_outside_tree(oid1, oid2):
    """
    Return True if oid2 outside of oid1 tree
    Used by SNMPSession.walk
    """
    try:
        if oid2.startswith(oid1):
            return False
        return True
    except:
        return True


class SNMPSession(object):
    """
    Session based, thread-safe interface
    """
    def __init__(self, peername, community, version=SNMP_VER['2c'], timeout=0.5, retries=1, debug=0): # pylint: disable=line-too-long
        self.debug = debug # 1 for partial debugging, 2 for full NETSNMP debugging
        self.version = version
        self.timeout = int(timeout*1000000) # seconds converted to microseconds
        self.retries = retries
        self.peername = peername
        self.community = community
        # Define session
        self.sess_ptr = netsnmp.create_session(self.version, self.timeout, self.retries,
                                               self.community, self.peername, self.debug)
        # Internal variables
        self._alive = True
        self._next = False

    def __enter__(self):
        """
        Support context (with SNMPSession(..) as ss..)
        """
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """
        Close session (clear file descriptors)
        """
        if netsnmp.close_session(self):
            self._alive = False

    def is_alive(self):
        return self._alive

    def get(self, oids):
        """
        Wrap netsnmp._api.get C function
        """
        # Define list to be populated by C API get()
        responses = []
        self._next = False

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
        Wrap netsnmp._api.get C function for GETNEXT
        """
        responses = []
        # Flag for GETNEXT
        self._next = True

        _rc = netsnmp.get(self, oids, responses)
        if not _rc:
            raise SNMPRuntimeError("Invalid return code", _rc)
        return responses

    def walk(self, oids):
        """
        Generator implementation of snmpwalk using self.getnext
        """
        if type(oids) is str:
            oids = [oids]
        for oid in oids:
            next_oid = oid
            while True:
                response = self.getnext(next_oid)[0]
                if oid_outside_tree(oid, response[OID]):
                    break
                elif response[TYPE] == "ENDOFMIBVIEW":
                    break
                elif response[TYPE] in SNMP_ERR:
                    raise netsnmp.SNMPError(response[TYPE], response[VALUE])
                next_oid = response[OID]
                yield response
