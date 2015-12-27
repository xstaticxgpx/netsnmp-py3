#!/usr/bin/env python3

from netsnmp._api import build_pdu

class SNMPDevice(object):

    def __init__(self, oids):

        # Ensure oids is list object
        # We expect OIDs to be an iterable of (name, oid) tuples
        assert type(oids)==list

        # Boilerplate
        self._oid2str = {}
        self._str2oid = {}

        # Do dict.update in order to allow subclass additions
        # Build dictionary of {oid: str,}
        self._str2oid.update(oids)
        # Populate reverse dictionary of {str: oid,}
        self._oid2str.update({oid: name for (name, oid) in oids})

        # Perform set comprehension to remove any duplicate entries
        self.oids = {oid for (name, oid) in oids}

        # Create PDU with the unique OIDs set, cloned by snmp_clone_pdu in get_async.c
        self.pdu = build_pdu(self.oids)

    def parse_oids(self, response):
        # Using this method we can alter parsing logic in subclasses

        # Responses come back as pipe delimited OID|TYPE|VALUE
        # We'll remove double quotes from responses by default
        ## WARNING! ascii-alike hex strings could have " characters within the value
        ## this is handled properly in subclasses.
        _vars = (var.replace('"', '').split('|', maxsplit=2) for var in response)

        # We don't normally need type
        return {self._oid2str[oid]: value for oid, type, value in _vars}
