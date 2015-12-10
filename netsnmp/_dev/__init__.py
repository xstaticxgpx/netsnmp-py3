#!/usr/bin/env python3

# Temporary devtype mapping
_DEVTYPES = {
    'archt01': 'model1',
    'archt02': 'model2',
    'archt03': 'model3',
    'archt04': 'model4',
    'archt05': 'model5',
}

# Update _DEVTYPES with reversed mapping, assumes keys and values are all unique
_DEVTYPES.update({v: k for (k, v) in _DEVTYPES.items()})


#class SNMPVarlist(list):
#    pass
#
#class SNMPVarbind(object):
#    def __init__(self, request=None):
#        # Request
#        self.request  = request
#        # Response attributes
#        self.response = None
#        self.typestr  = None
#        self.oid      = None

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

#SNMP_DEVTYPES = {
#    'model1': SNMPDevice_model1(),
#    'model2': SNMPDevice_model2(),
#    'model3': SNMPDevice_model3(),
#    'model4': SNMPDevice_model4(),
#    'model5': SNMPDevice_model5(),
#    '__default__': SNMPDevice(),
#}
#
#def SNMPClassify(host, community, devtype=None):
#    # Check for specific before generic
#    try:
#        return (host, community, _DEVTYPES[host], SNMP_DEVTYPES[_DEVTYPES[host]])
#    except KeyError:
#        for key in SNMP_DEVTYPES:
#            if host == key:
#                return (host, community, key, SNMP_DEVTYPES[key])
#        return (host, community, '__default__', SNMP_DEVTYPES['__default__'])
