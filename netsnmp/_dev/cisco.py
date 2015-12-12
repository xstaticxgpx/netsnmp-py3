#!/usr/bin/env python3

from . import SNMPDevice

class SNMPCiscoDevice(SNMPDevice):

    def __init__(self, oids=None):

        # Sorted list of set(name, oid)
        self._oids = [
            ('sysDescr', '.1.3.6.1.2.1.1.1.0'),
            #('sysUptime', '.1.3.6.1.2.1.1.3.0'),
        ]

        if oids:
            assert type(oids) == list
            # Append any extra OIDs
            self._oids+=oids
        SNMPDevice.__init__(self, oids=self._oids)

    # For demonstration purposes, this is how we can parse oids different in subclass
    def parse_oids(self, response):
        _vars = [var.split('=', maxsplit=1) for var in response]

        # This is where we vary from SNMPDevice
        # e.g., remove double quotes from string responses
        _vars = [(oid, value.replace('"', '')) for (oid, value) in _vars]

        return {self._str2oid[oid]: value for (oid, value) in _vars}
