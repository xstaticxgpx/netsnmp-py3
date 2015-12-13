#!/usr/bin/env python3

class SNMPDevice(object):

    def __init__(self, oids):
        # Boilerplate
        self._oid2str = {}
        self._str2oid = {}

        # We expect OIDs to be an iterable of (name, oid) tuples
        self.oids = [oid for (name, oid) in oids]

        # Do dict.update in order to allow subclass additions
        # Build dictionary of oid: str
        self._str2oid.update(oids)
        # Populate reverse dictionary of str: oid
        self._oid2str.update({oid: name for (name, oid) in oids})

    def parse_oids(self, response):
        _vars = [var.split('=', maxsplit=1) for var in response]
        return {self._oid2str[oid]: value for (oid, value) in _vars}
