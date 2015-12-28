import netsnmp
from netsnmp._dev import arris, cisco, technicolor

# Standardized element names
PRIMARY_TUNNEL='priRemoteHost'
SECONDARY_TUNNEL='secRemoteHost'
WAN_DSCP='wanDscp'
BSSID_24='bssSSID24'
BSSID_50='bssSSID50'
ISOLATE_24='apIsolation24'
ISOLATE_50='apIsolation50'
ENABLED_24='bssEnable24'
ENABLED_50='bssEnable50'
CLOSEDN_24='bssClosedNetwork24'
CLOSEDN_50='bssClosedNetwork50'
HOTSPOT_EN='hotspotEnabled'

# temporary
SNMP_DEVTYPES = {
        'DPC3939': cisco.SNMPCiscoDevice([
            # RDK?
            (PRIMARY_TUNNEL,    '.1.3.6.1.4.1.1429.79.2.14.1.3.0'),
            (SECONDARY_TUNNEL,  '.1.3.6.1.4.1.1429.79.2.14.1.5.0'),
            (WAN_DSCP,          '.1.3.6.1.4.1.1429.79.2.14.1.6.0'),
            (ENABLED_24,        '.1.3.6.1.4.1.1429.79.2.2.2.1.1.2.34'),
            (BSSID_24,          '.1.3.6.1.4.1.1429.79.2.2.2.1.1.3.34'),
            (CLOSEDN_24,        '.1.3.6.1.4.1.1429.79.2.2.2.1.1.5.34'),
            (ISOLATE_24,        '.1.3.6.1.4.1.1429.79.2.2.2.1.1.15.34'),
            (ENABLED_50,        '.1.3.6.1.4.1.1429.79.2.2.2.1.1.2.114'),
            (BSSID_50,          '.1.3.6.1.4.1.1429.79.2.2.2.1.1.3.114'),
            (CLOSEDN_50,        '.1.3.6.1.4.1.1429.79.2.2.2.1.1.5.114'),
            (ISOLATE_50,        '.1.3.6.1.4.1.1429.79.2.2.2.1.1.15.114'),
            (HOTSPOT_EN,        '.1.3.6.1.4.1.1429.79.2.13.1.1.0'),
            # this oid seems to increase response time unreasonably
            #('wifiChannel', '.1.3.6.1.4.1.1429.79.2.2.6.1.1.3.32'),
        ]), #hexconvert=['.1.3.6.1.2.1.55.1.5.1.8.2']), Can define hexconvert here or in netsnmp/_dev/cisco.py, etc files
        'TC8305C': technicolor.SNMPTechnicolorDevice([
            (PRIMARY_TUNNEL,    '.1.3.6.1.4.1.4413.2.2.2.1.7.3.1.3.0'),
            (SECONDARY_TUNNEL,  '.1.3.6.1.4.1.4413.2.2.2.1.7.3.1.5.0'),
            (WAN_DSCP,          '.1.3.6.1.4.1.4413.2.2.2.1.7.3.1.6.0'),
            ('bssADDR24',       '.1.3.6.1.2.1.2.2.1.6.10003'),
            (ENABLED_24,        '.1.3.6.1.4.1.2863.205.200.1.10.8.6.0'),
            (BSSID_24,          '.1.3.6.1.4.1.4413.2.2.2.1.18.1.2.1.1.3.10003'),
            (CLOSEDN_24,        '.1.3.6.1.4.1.4413.2.2.2.1.18.1.2.1.1.5.10003'),
        ]),
        'TG852G': arris.SNMPArrisDevice([
            ('wanEnabled',      '.1.3.6.1.4.1.4115.1.20.1.1.1.19.1.1.1.1'),
            (PRIMARY_TUNNEL,    '.1.3.6.1.4.1.4115.1.20.1.1.1.19.1.1.4.1'),
            (SECONDARY_TUNNEL,  '.1.3.6.1.4.1.4115.1.20.1.1.1.19.1.1.6.1'),
            (WAN_DSCP,          '.1.3.6.1.4.1.4115.1.20.1.1.1.19.1.1.19.1'),
            ('bssADDR24',       '.1.3.6.1.4.1.4115.1.20.1.1.3.22.1.1.3'),
            (BSSID_24,          '.1.3.6.1.4.1.4115.1.20.1.1.3.22.1.2.3'),
            ('bssActive24',     '.1.3.6.1.4.1.4115.1.20.1.1.3.22.1.3.3'),
            (ENABLED_24,        '.1.3.6.1.4.1.4115.1.20.1.1.3.22.1.4.3'),
            ('wifiChannel24',   '.1.3.6.1.4.1.4115.1.20.1.1.3.2.0'),
        ]),
        'TG1682G': arris.SNMPArrisDevice([
            # RDK?
            (PRIMARY_TUNNEL,    '.1.3.6.1.4.1.17270.50.2.14.1.3.0'),
            (SECONDARY_TUNNEL,  '.1.3.6.1.4.1.17270.50.2.14.1.5.0'),
            (WAN_DSCP,          '.1.3.6.1.4.1.17270.50.2.14.1.6.0'),
            (ENABLED_24,        '.1.3.6.1.4.1.17270.50.2.2.2.1.1.2.10003'),
            (BSSID_24,          '.1.3.6.1.4.1.17270.50.2.2.2.1.1.3.10003'),
            (CLOSEDN_24,        '.1.3.6.1.4.1.17270.50.2.2.2.1.1.5.10003'),
            (ISOLATE_24,        '.1.3.6.1.4.1.17270.50.2.2.2.1.1.15.10003'),
            (ENABLED_50,        '.1.3.6.1.4.1.17270.50.2.2.2.1.1.2.10103'),
            (BSSID_50,          '.1.3.6.1.4.1.17270.50.2.2.2.1.1.3.10103'),
            (CLOSEDN_50,        '.1.3.6.1.4.1.17270.50.2.2.2.1.1.5.10103'),
            (ISOLATE_50,        '.1.3.6.1.4.1.17270.50.2.2.2.1.1.15.10103'),
            (HOTSPOT_EN,        '.1.3.6.1.4.1.17270.50.2.13.1.1.0'),
        ]),
        'Belair': netsnmp._dev.SNMPDevice([
            ('model', '.1.3.6.1.2.1.1.1.0'),
            ('serial_number', '.1.3.6.1.4.1.15768.3.1.1.11.2.0'),
            ('tunnel_peer1', '.1.3.6.1.4.1.15768.5.1.1.2.1.5.1.1'),
            ('tunnel_peer2', '.1.3.6.1.4.1.15768.5.1.1.2.1.9.1.1'),
            ('swbank_active', '.1.3.6.1.4.1.15768.3.1.1.3.1.0'),
            ('swbank_next', '.1.3.6.1.4.1.15768.3.1.1.3.2.0'),
            ('software_a', '.1.3.6.1.4.1.15768.3.1.1.3.5.1.2.1'),
            ('software_b', '.1.3.6.1.4.1.15768.3.1.1.3.5.1.2.2'),
            ('tunnel_status', '.1.3.6.1.4.1.15768.5.1.1.3.1.1.1.1'),
            ('vpn_label', '.1.3.6.1.4.1.15768.5.1.1.2.1.2.1.1'),
            ('tunnel1_active', '.1.3.6.1.4.1.15768.5.1.1.3.1.3.1.1'),
            ('tunnel2_active', '.1.3.6.1.4.1.15768.5.1.1.3.1.4.1.1'),
            ('radius_server1', '.1.3.6.1.2.1.67.1.2.1.1.3.1.2.1'),
            ('radius_server2', '.1.3.6.1.2.1.67.1.2.1.1.3.1.2.2'),
            #('cm.software', '.1.3.6.1.4.1.15768.6.4.1.1.1.5.1'),
        ]),
        '__other__': cisco.SNMPCiscoDevice([
            ('sysDescr', '.1.3.6.1.2.1.1.1.0'),
            ('sysUptime', '.1.3.6.1.2.1.1.3.0'),
            ('macAddr', '.1.3.6.1.2.1.55.1.5.1.8.2'),
        ], hexconvert=['.1.3.6.1.2.1.55.1.5.1.8.2']),# Can define hexconvert here or in netsnmp/_dev/cisco.py, etc files
}

# Cisco pointers
SNMP_DEVTYPES['DPC3939B'] = SNMP_DEVTYPES['DPC3939']
SNMP_DEVTYPES['DPC3941B'] = SNMP_DEVTYPES['DPC3939']
SNMP_DEVTYPES['DPC3941T'] = SNMP_DEVTYPES['DPC3939']
# Arris pointers
SNMP_DEVTYPES['TG862G'] = SNMP_DEVTYPES['TG852G']
