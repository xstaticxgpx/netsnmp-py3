#!/usr/bin/env python3

class SNMPDevice(object):

    def __init__(self, oids):
        self.maxoids = 128
        # Do dict.update in order to allow subclassing hierarchy
        self._oid_mapping = {}
        self._oid_mapping.update(oids)
        self.oids = [oid for (name, oid) in oids]

        # Populate reverse mapping
        self._str_mapping = {}
        self._str_mapping.update({oid: name for (name, oid) in oids})

    def parse_oids(self, response):
        _vars = [var.split('=', maxsplit=1) for var in response]
        return (len(_vars), {self._str_mapping[oid]: value for (oid, value) in _vars})

