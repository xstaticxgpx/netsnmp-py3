#!/usr/bin/env python3

from . import SNMPDevice
from netsnmp import snmp_hex2str

class SNMPTechnicolorDevice(SNMPDevice):

    def __init__(self, oids=[], hexconvert=[]):

        # Ordered list of tuple(name, oid)
        self._oids = []
        
        # Set of OIDs that require manual hex conversion
        self._hexconvert = [
            # priRemoteHost
            '.1.3.6.1.4.1.4413.2.2.2.1.7.3.1.3.0',
            # secRemoteHost
            '.1.3.6.1.4.1.4413.2.2.2.1.7.3.1.5.0',
            # bssADDR24
            '.1.3.6.1.2.1.2.2.1.6.10003',
        ]

        if oids:
            # Append any extra OIDs passed
            self._oids+=oids
        if hexconvert:
            # Append any extra OIDs requiring conversion
            # get unique set using bitwise or
            self._hexconvert = set(self._hexconvert) | set(hexconvert)

        # Instantiate from parent
        SNMPDevice.__init__(self, oids=self._oids)

    # For demonstration purposes, this is how we can parse oids different in subclass
    def parse_oids(self, response):
        # Responses come back as pipe delimited OID|TYPE|VALUE
        _vars = (var.split('|', maxsplit=2) for var in response)

        # This is where we vary from SNMPDevice
        # e.g., create genexpr to work on _hexconvert oids
        _vars = ((oid,
                  snmp_hex2str(type, value)[1] if oid in self._hexconvert else
                  value.replace('"', '')) for oid, type, value in _vars)

        return {self._oid2str[oid]: value for oid, value in _vars}
