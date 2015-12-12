import netsnmp
from netsnmp._dev import cisco

# temporary
SNMP_DEVTYPES = {
        'archt01': cisco.SNMPCiscoDevice([
            ('sysHostname', '.1.3.6.1.2.1.1.5.0'),
        ]),
        'archt02': cisco.SNMPCiscoDevice(),
        'archt03': cisco.SNMPCiscoDevice([
            ('1min', '.1.3.6.1.4.1.2021.10.1.3.1'),
            #('5min', '.1.3.6.1.4.1.2021.10.1.3.2'),
            #('15min', '.1.3.6.1.4.1.2021.10.1.3.3'),
            ]),
        'archt04': cisco.SNMPCiscoDevice([
            #('1min', '.1.3.6.1.4.1.2021.10.1.3.1'),
            ('5min', '.1.3.6.1.4.1.2021.10.1.3.2'),
            #('15min', '.1.3.6.1.4.1.2021.10.1.3.3'),
        ]),
        'archt05': netsnmp._dev.SNMPDevice([
            ('sysDescr', '.1.3.6.1.2.1.1.1.0'),
            #('1min', '.1.3.6.1.4.1.2021.10.1.3.1'),
            #('5min', '.1.3.6.1.4.1.2021.10.1.3.2'),
            ('15min', '.1.3.6.1.4.1.2021.10.1.3.3'),
        ]),
}

