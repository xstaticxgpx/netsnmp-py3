#!/usr/bin/env python3

# Temporary devtype mapping
_DEVTYPES = {
    'archt01': 'model1',
    'archt02': 'model2',
    'archt03': 'model3',
    'archt04': 'model4',
    'archt05': 'model5',
}


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
    # Default OIDs
    _oid_mapping = {
        'sysDescr': '.1.3.6.1.2.1.1.1.0',
        'sysUptime': '.1.3.6.1.2.1.1.3.0',
    }

    def __init__(self, maxoids=None):
        # Request attributes
        self.maxoids = maxoids
        self.oids = list(self._oid_mapping.values())
        self._inverted_oid_mapping = {v: k for (k, v) in self._oid_mapping.items()}
        # Response attributes
        self.response = None
        self.typestr = None
        self.oid = None

    def parse_oids(self, response):
        vars = [var.split('=', maxsplit=1) for var in response]
        return (len(vars), {self._inverted_oid_mapping[oid]: value for (oid, value) in vars})

class SNMPDevice_model1(SNMPDevice):
    _oid_mapping = {
        'sysDescr': '.1.3.6.1.2.1.1.1.0',
    }

    def __init__(self):
        SNMPDevice.__init__(self)

class SNMPDevice_model2(SNMPDevice):
    _oid_mapping = {
        'sysUptime': '.1.3.6.1.2.1.1.3.0',
    }

    def __init__(self):
        SNMPDevice.__init__(self)

class SNMPDevice_model3(SNMPDevice):
    _oid_mapping = {
        'test1': '.1.3.6.1.2.1.1.5.0',
    }

    def __init__(self):
        SNMPDevice.__init__(self)

class SNMPDevice_model4(SNMPDevice):
    _oid_mapping = {
        'test2': '.1.3.6.1.2.1.1.7.0',
        'test3': '.1.3.6.1.2.1.1.11.0',
    }

    def __init__(self):
        SNMPDevice.__init__(self)

class SNMPDevice_model5(SNMPDevice):
    _oid_mapping = {
        'test4': '.1.3.6.1.2.1.1.9.0',
    }

    def __init__(self):
        SNMPDevice.__init__(self)

SNMP_DEVTYPES = {
#    'model1': SNMPDevice_model1(),
#    'model2': SNMPDevice_model2(),
#    'model3': SNMPDevice_model3(),
#    'model4': SNMPDevice_model4(),
#    'model5': SNMPDevice_model5(),
    '__default__': SNMPDevice(),
}

def SNMPClassify(host, community, devtype=None):
    # Check for specific before generic
    try:
        return (host, community, _DEVTYPES[host], SNMP_DEVTYPES[_DEVTYPES[host]])
    except KeyError:
        for key in SNMP_DEVTYPES:
            if key in host:
                return (host, community, key, SNMP_DEVTYPES[key])
        return (host, community, '__default__', SNMP_DEVTYPES['__default__'])
