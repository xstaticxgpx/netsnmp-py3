#!/usr/bin/env python3

from netsnmp._api import build_pdu

class SNMPDevice(object):

    def __init__(self, oids=[]):

        # Ensure oids is an iterable object
        # We expect oids to be any iterable of (name, oid) tuples
        assert type(oids)==set or \
               type(oids)==list or \
               type(oids)==tuple

        # Boilerplate
        self._str2oid = {}
        self._oid2str = {}
        ## Do dict.update in order to allow subclass additions
        self._str2oid.update(oids)
        self._oid2str.update({oid: name for (name, oid) in oids})

        # Perform set comprehension to remove any duplicate entries
        self._oids = {oid for (name, oid) in oids}

        # Create PDU with the unique OIDs set
        # returns void pointer which is passed to snmp_clone_pdu in get_async.c
        self.pdu = build_pdu(self._oids)

    def parse_oids(self, response):
        # Using this method we can alter parsing logic in subclasses

        # Responses come back as pipe delimited OID|TYPE|VALUE
        # We'll remove double quotes from responses by default
        ## WARNING! ascii-alike hex strings could have " characters within the value
        ## this is handled properly in subclasses.
        _vars = (var.replace('"', '').split('|', 2) for var in response)

        # We don't normally need type
        return {self._oid2str[oid]: value for oid, type, value in _vars}
