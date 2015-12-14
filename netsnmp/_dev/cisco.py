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
            # Append any extra OIDs passed
            self._oids+=oids
        SNMPDevice.__init__(self, oids=self._oids)

    # For demonstration purposes, this is how we can parse oids different in subclass
    def parse_oids(self, response):
        # Responses come back as pipe delimited OID|TYPE|VALUE
        _vars = [tuple(var.split('|', maxsplit=2)) for var in response]

        # This is where we vary from SNMPDevice
        # e.g., remove double quotes from string responses
        _vars = [(oid, type, value.replace('"', '')) for oid, type, value in _vars]

        return {self._oid2str[oid]: (type, value) for oid, type, value in _vars}
