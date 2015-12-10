#!/usr/bin/env python3

from . import SNMPDevice

class SNMPCiscoDevice(SNMPDevice):

    def __init__(self, oids=None):

        # Sorted list of set(name, oid)
        self._oids = [
            ('sysDescr', '.1.3.6.1.2.1.1.1.0'),
            ('sysUptime', '.1.3.6.1.2.1.1.3.0'),
        ]

        if oids:
            assert type(oids) == list
            # Append any extra OIDs
            self._oids+=oids
        print(self._oids)
        SNMPDevice.__init__(self, oids=self._oids)
