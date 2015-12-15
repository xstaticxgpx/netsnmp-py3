#!/usr/bin/env python3

from . import SNMPDevice
from netsnmp import snmp_hex2str

class SNMPCiscoDevice(SNMPDevice):

    def __init__(self, oids=[], hexconvert=[]):

        # Sorted list of set(name, oid)
        self._oids = [
            ('sysDescr', '.1.3.6.1.2.1.1.1.0'),
            ('sysUptime', '.1.3.6.1.2.1.1.3.0'),
        ]
        
        # Set of OIDs that require manual hex conversion
        self._hexconvert = [
            '.1.3.6.1.2.1.55.1.5.1.8.2',
        ]

        if oids:
            # Append any extra OIDs passed
            self._oids+=oids
        if hexconvert:
            # Append any extra OIDs requiring conversion
            # get unique set using bitwise or
            self._hexconvert = set(self._hexconvert) | set(hexconvert)
            print(self._hexconvert)
        SNMPDevice.__init__(self, oids=self._oids)

    # For demonstration purposes, this is how we can parse oids different in subclass
    def parse_oids(self, response):
        # Responses come back as pipe delimited OID|TYPE|VALUE
        _vars = [tuple(var.split('|', maxsplit=2)) for var in response]

        # This is where we vary from SNMPDevice
        # e.g., remove double quotes from string responses and work on _hexconvert oids
        _vars = [(oid,
                  snmp_hex2str('Hex', value)[1] if oid in self._hexconvert else value.replace('"', '')) for oid, value in _vars]

        return {self._oid2str[oid]: value for oid, value in _vars}
