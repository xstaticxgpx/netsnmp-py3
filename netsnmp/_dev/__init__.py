#!/usr/bin/env python3

class SNMPDevice(object):

    def __init__(self, oids):

        # Ensure oids is list object
        assert type(oids)==list

        # Boilerplate
        self._oid2str = {}
        self._str2oid = {}

        # We expect OIDs to be an iterable of (name, oid) tuples
        # Perform set comprehension to remove any duplicate entries
        self.oids = {oid for (name, oid) in oids}

        # Do dict.update in order to allow subclass additions
        # Build dictionary of {oid: str,}
        self._str2oid.update(oids)
        # Populate reverse dictionary of {str: oid,}
        self._oid2str.update({oid: name for (name, oid) in oids})

    def parse_oids(self, response):
        # Using this method we can alter parsing logic in subclasses

        # Responses come back as pipe delimited OID|TYPE|VALUE
        _vars = [tuple(var.split('|', maxsplit=2)) for var in response]

        return {self._oid2str[oid]: (type, value) for oid, type, value in _vars}
