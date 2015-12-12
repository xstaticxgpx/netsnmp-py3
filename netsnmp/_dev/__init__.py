#!/usr/bin/env python3

class SNMPDevice(object):

    def __init__(self, oids):
        # Max OIDs per request
        self.maxoids = 128
        # Do dict.update in order to allow subclass additions
        self._oid2str = {}
        self._oid2str.update(oids)
        self.oids = [oid for (name, oid) in oids]
        #print(self.oids)

        # Populate reverse mapping
        self._str2oid = {}
        self._str2oid.update({oid: name for (name, oid) in oids})

    def parse_oids(self, response):
        _vars = [var.split('=', maxsplit=1) for var in response]
        return {self._str2oid[oid]: value for (oid, value) in _vars}
