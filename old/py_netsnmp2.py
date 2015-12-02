#!/usr/bin/env python3

import ctypes, ctypes.util
#import gc
import time

#gc.disable()

SNMP_VERSION_2c=2
POINTER = ctypes.POINTER

# include/net-netsnmp_library/oid.h
c_oid   = ctypes.c_ulong
c_oid_p = ctypes.POINTER(c_oid)

# Short type variables
_sint  = ctypes.c_short
_usint = ctypes.c_ushort
_int   = ctypes.c_long
_uint  = ctypes.c_ulong
_float = ctypes.c_float
_size  = ctypes.c_size_t
_char  = ctypes.c_char
_uchar = ctypes.c_ubyte
_str   = ctypes.c_wchar
_double= ctypes.c_double

# Pointer type variables
c_void_p = ctypes.c_void_p
c_char_p = ctypes.c_char_p
#c_char_p  = POINTER(_char)
c_sizet_p = POINTER(_size)

netsnmp = ctypes.cdll.LoadLibrary(ctypes.util.find_library("netsnmp"))

# include/net-netsnmp_library/asn1.h
ASN_INTEGER                             = 0x02
ASN_OCTET_STR                           = 0x04
ASN_APPLICATION                         = 0x40

# counter64 requires some extra work because it can't be reliably represented
# by a single C data type
class counter64(ctypes.Structure):
    @property
    def value(self):
        return self.high << 32 | self.low

    @value.setter
    def value(self, val):
        self.high = val >> 32
        self.low  = val & 0xFFFFFFFF

    def __init__(self, initval=0):
        ctypes.Structure.__init__(self, 0, 0)
        self.value = initval
counter64_p = ctypes.POINTER(counter64)
counter64._fields_ = [
    ("high",                ctypes.c_ulong),
    ("low",                 ctypes.c_ulong)
]

# include/net-netsnmp_library/snmp_impl.h
ASN_IPADDRESS                           = ASN_APPLICATION | 0
ASN_COUNTER                             = ASN_APPLICATION | 1
ASN_UNSIGNED                            = ASN_APPLICATION | 2
ASN_TIMETICKS                           = ASN_APPLICATION | 3
ASN_COUNTER64                           = ASN_APPLICATION | 6

# include/net-netsnmp_types.h
MAX_OID_LEN                             = 128

class netsnmp_vardata(ctypes.Union): pass
netsnmp_vardata._fields_ = [
    ('integer', POINTER(_int)),
    ('string', POINTER(_uchar)),
    ('objid', c_oid_p),
    ('bitstring', POINTER(_uchar)),
    ('counter64', counter64_p),
    ('floatVal', _float),
    ('doubleVal', _double),
]

class netsnmp_variable_list(ctypes.Structure): pass
netsnmp_variable_list_p = POINTER(netsnmp_variable_list)
netsnmp_variable_list_p_p = POINTER(netsnmp_variable_list_p)
netsnmp_variable_list._fields = [
    ('next_variable', netsnmp_variable_list_p),
    ('name', c_oid_p),
    ('name_len', _size),
    ('type', _uchar),
    ('val', netsnmp_vardata),
    ('val_len', _size),
    ('name_loc', c_oid, MAX_OID_LEN),
    ('buf', _uchar),
    ('data', c_void_p),
    ('dataFreeHook', c_void_p),
    ('index', _int)
]


class netsnmp_mib_handler(ctypes.Structure): pass
netsnmp_mib_handler_p = POINTER(netsnmp_mib_handler)

class netsnmp_log_message(ctypes.Structure): pass
netsnmp_log_message_p = POINTER(netsnmp_log_message)
netsnmp_log_message._fields_=[('priority', _int),
                           ('msg', c_char_p)]

class netsnmp_session(ctypes.Structure): pass
netsnmp_session_p          = POINTER(netsnmp_session)
netsnmp_session._fields_   = [
    ('version', _int),
    ('retries', _int),
    ('timeout', _int),
    ('flags',   _uint),
    ('subsession', netsnmp_session_p),
    ('next', netsnmp_session_p),
    ('peername', c_char_p),
    ('remote_port', _uint),
    ('localname', c_char_p),
    ('local_port', _uint),
    ('authenticator', _uchar),
    ('callback', _int),
    ('callback_magic', c_void_p),
    ('s_errno', _int),
    ('s_snmp_errno', _int),
    ('sessid', _int),
    ('community', c_char_p),
    ('community_len', _size),
    ('rcvMsgMaxSize', _size),
    ('sndMsgMaxSize', _size),
    ('isAuthoritative', _uchar),
    ('contextEngineID', POINTER(_uchar)),
    ('contextEngineIDLen', _size),
    ('engineBoots', _uint),
    ('engineTime', _uint),
    ('contextName', c_char_p),
    ('contextNameLen', _size),
    ('securityEngineID', POINTER(_uchar)),
    ('securityEngineIDLen', _size),
    ('securityName', c_char_p),
    ('securityNameLen', _size),
    ('securityAuthProto', c_oid_p),
    ('securityAuthProtoLen', _size),
    ('securityAuthKey', _uchar),
    ('securityAuthKeyLen', _size),
    ('securityAuthLocalKey', POINTER(_uchar)),
    ('securityAuthLocalKeyLen', _size),
    ('securityPrivProto', c_oid_p),
    ('securityPrivProtoLen', _size),
    ('securityPrivKey', _uchar),
    ('securityPrivKeyLen', _size),
    ('securityPrivLocalKey', POINTER(_uchar)),
    ('securityPrivLocalKeyLen', _size),
    ('securityModel', _int),
    ('securityLevel', _int),
    ('paramName', c_char_p),
    ('securityInfo', c_void_p),
    ('myvoid', c_void_p),
]
    
class netsnmp_pdu(ctypes.Structure): pass
netsnmp_pdu_p              = POINTER(netsnmp_pdu)
netsnmp_pdu_p_p            = POINTER(netsnmp_pdu_p)
netsnmp_pdu._fields_       = [
    ('version', _int),
    ('command', _int),
    ('reqid', _int),
    ('msgid', _int),
    ('transid', _int),
    ('sessid', _int),
    ('errstat', _int),
    ('errindex', _int),
    ('time', _uint),
    ('flags', _uint),
    ('securityModel', _int),
    ('securityLevel', _int),
    ('msgParseModel', _int),
    ('transport_data', c_void_p),
    ('transport_data_length', _int),
    ('tDomain', c_oid_p),
    ('tDomainLen', _size),
    ('variables', netsnmp_variable_list_p),
    ('community', POINTER(_uchar)),
    ('community_len', _size),
    ('enterprise', c_oid_p),
    ('enterprise_len', _size),
    ('trap_type', _int),
    ('specific_type', _int),
    ('agent_addr', _uchar),
    ('contextEngineID', POINTER(_uchar)),
    ('contextEngineIDLen', _size),
    ('contextName', c_char_p),
    ('contextNameLen', _size),
    ('securityEngineID', POINTER(_uchar)),
    ('securityEngineIDLen', _size),
    ('securityName', c_char_p),
    ('securityNameLen', _size),
    ('priority', _int),
    ('range_subid', _int),
    ('securityStateRef', c_void_p),
]



# include/net-netsnmp_library/parse.h
class tree(ctypes.Structure): pass

# include/net-netsnmp_varbind_api.h
for f in [ netsnmp.snmp_varlist_add_variable ]:
    f.argtypes = [
        netsnmp_variable_list_p_p,       # netsnmp_variable_list **varlist
        c_oid_p,                         # const oid *name
        ctypes.c_size_t,                 # size_t name_length
        ctypes.c_ubyte,                  # u_char type
        ctypes.c_void_p,                 # const void *value
        ctypes.c_size_t                  # size_t len
    ]
    f.restype = netsnmp_variable_list_p

# Workaround for net-netsnmp_5.4.x that has a bug with unresolved dependencies
# in its libraries (http://sf.net/p/net-netsnmp_bugs/2107): load netsnmphelpers
# first
#try:
#    libnsh = ctypes.cdll.LoadLibrary(ctypes.util.find_library("netsnmp_elpers"))
#except:
#    raise Exception("Could not load libnetsnmp_elpers! Is net-snmp installed?")
#try:
#    libnsa = ctypes.cdll.LoadLibrary(ctypes.util.find_library("netsnmp_gent"))
#except:
#    raise Exception("Could not load libnetsnmp_gent! Is net-snmp installed?")

# net-netsnmp_<5.6.x had various functions in libnetsnmphelpers.so that were moved
# to libnetsnmp_gent.so in later versions. Use netsnmp_create_watcher_info as
# a test and define a libnsX handle to abstract from the actually used library
# version.
#try:
#    libnsa.netsnmp_create_watcher_info
#    netsnmp_= libnsa
#except AttributeError:
#    netsnmp_= libnsh

# include/net-netsnmp_library/callback.h

# Callback major types 
SNMP_CALLBACK_LIBRARY                   = 0
SNMP_CALLBACK_APPLICATION               = 1

# netsnmp_CALLBACK_LIBRARY minor types 
SNMP_CALLBACK_LOGGING                   = 4

SNMPCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                       # result type
    ctypes.c_int,                       # int majorID
    ctypes.c_int,                       # int minorID
    ctypes.c_void_p,                    # void *serverarg
    ctypes.c_void_p                     # void *clientarg
)

for f in [ netsnmp.snmp_register_callback ]:
    f.argtypes = [
        ctypes.c_int,                   # int major
        ctypes.c_int,                   # int minor
        SNMPCallback,                   # SNMPCallback *new_callback
        ctypes.c_void_p                 # void *arg
    ]
    f.restype = int

# include/net-netsnmp_agent/agent_callbacks.h
SNMPD_CALLBACK_INDEX_STOP               = 11

# include/net-netsnmp_library/snmp_logging.h
LOG_EMERG                               = 0 # system is unusable
LOG_ALERT                               = 1 # action must be taken immediately
LOG_CRIT                                = 2 # critical conditions
LOG_ERR                                 = 3 # error conditions
LOG_WARNING                             = 4 # warning conditions
LOG_NOTICE                              = 5 # normal but significant condition
LOG_INFO                                = 6 # informational
LOG_DEBUG                               = 7 # debug-level messages

# include/net-netsnmp_library/snmp_api.h
SNMPERR_SUCCESS                         = 0

# include/net-netsnmp_library/default_store.h
NETSNMP_DS_LIBRARY_ID                   = 0
NETSNMP_DS_APPLICATION_ID               = 1
NETSNMP_DS_LIB_PERSISTENT_DIR           = 8

for f in [ netsnmp.netsnmp_ds_set_boolean ]:
    f.argtypes = [
        ctypes.c_int,                   # int storeid
        ctypes.c_int,                   # int which
        ctypes.c_int                    # int value
    ]
    f.restype = ctypes.c_int

for f in [ netsnmp.netsnmp_ds_set_string ]:
    f.argtypes = [
        ctypes.c_int,                   # int storeid
        ctypes.c_int,                   # int which
        ctypes.c_char_p                 # const char *value
    ]
    f.restype = ctypes.c_int

# include/net-netsnmp_agent/ds_agent.h
NETSNMP_DS_AGENT_ROLE                   = 1
NETSNMP_DS_AGENT_X_SOCKET               = 1

# include/net-netsnmp_library/snmp.h
SNMP_ERR_NOERROR                        = 0

for f in [ netsnmp.init_snmp ]:
    f.argtypes = [
        ctypes.c_char_p                 # const char *type
    ]
    f.restype = None

for f in [ netsnmp.snmp_shutdown ]:
    f.argtypes = [
        ctypes.c_char_p                 # const char *type
    ]
    f.restype = None

for f in [ netsnmp.snmp_pdu_create ]:
    f.argtypes = [
        ctypes.c_int
    ]
    f.restype = netsnmp_pdu_p

# include/net-snmp/session_api.h

for f in [ netsnmp.snmp_sess_init ]:
    f.argtypes = [
        netsnmp_session_p
    ]
    f.restype = None

for f in [ netsnmp.snmp_sess_open ]:
    f.argtypes = [
        netsnmp_session_p
    ]
    f.restype = c_void_p

for f in [ netsnmp.snmp_sess_session ]:
    f.argtypes = [
        c_void_p
    ]
    f.restype = netsnmp_session_p

for f in [ netsnmp.snmp_open ]:
    f.argtypes = [
        netsnmp_session_p
    ]
    f.restype = netsnmp_session_p

for f in [ netsnmp.snmp_synch_response ]:
    f.argtypes = [
        netsnmp_session_p,
        netsnmp_pdu_p,
        netsnmp_pdu_p_p,
    ]
    f.restype = ctypes.c_int

for f in [ netsnmp.snmp_close ]:
    f.argtypes = [
        netsnmp_session_p
    ]
    f.restype = ctypes.c_int

for f in [ netsnmp.snmp_add_null_var ]:
    f.argtypes = [
        netsnmp_pdu_p,
        c_oid_p,
        ctypes.c_size_t,
    ]
    f.restype = netsnmp_variable_list_p


# include/net-netsnmp_agent/snmp_vars.h
#for f in [ netsnmp_init_agent ]:
#    f.argtypes = [
#        ctypes.c_char_p                 # const char *app
#    ]
#    f.restype = ctypes.c_int

#for f in [ netsnmp_shutdown_agent ]:
#    f.argtypes = None
#    f.restype = ctypes.c_int

# include/net-netsnmp_mib_api.h
#for f in [ netsnmp.snmp_init_mib ]:
#    f.argtypes = None
#    f.restype = None
#
#for f in [ netsnmp.read_mib ]:
#    f.argtypes = [
#        ctypes.c_char_p                 # const char *filename
#    ]
#    f.restype = ctypes.POINTER(tree)

for f in [ netsnmp.get_node ]:
    f.argtypes = [
        c_char_p,
        c_oid_p,
        c_sizet_p,
    ]
    f.restype = ctypes.c_int

for f in [ netsnmp.read_objid ]:
    f.argtypes = [
        ctypes.c_char_p,                # const char *input
        c_oid_p,                        # oid *output
        c_sizet_p                       # size_t *out_len
    ]
    f.restype = ctypes.c_int

# include/net-netsnmp_agent/agent_handler.h
#HANDLER_CAN_GETANDGETNEXT               = 0x01
#HANDLER_CAN_SET                         = 0x02
#HANDLER_CAN_RONLY                       = HANDLER_CAN_GETANDGETNEXT
#HANDLER_CAN_RWRITE                      = (HANDLER_CAN_GETANDGETNEXT | \
#                                           HANDLER_CAN_SET)
#for f in [ netsnmp_netsnmp_create_handler_registration ]:
#    f.argtypes = [
#        ctypes.c_char_p,                # const char *name
#        ctypes.c_void_p,                # netsnmp_Node_Handler *handler_access_method
#        c_oid_p,                        # const oid *reg_oid
#        ctypes.c_size_t,                # size_t reg_oid_len
#        ctypes.c_int                    # int modes
#    ]
#    f.restype = netsnmp_handler_registration_p


# include/net-netsnmp_agent/watcher.h
#WATCHER_FIXED_SIZE                      = 0x01
#WATCHER_MAX_SIZE                        = 0x02
#
#class netsnmp_watcher_info(ctypes.Structure): pass
#netsnmp_watcher_info_p = ctypes.POINTER(netsnmp_watcher_info)
#netsnmp_watcher_info._fields_ = [
#    ("data",                ctypes.c_void_p),
#    ("data_size",           ctypes.c_size_t),
#    ("max_size",            ctypes.c_size_t),
#    ("type",                ctypes.c_ubyte),
#    ("flags",               ctypes.c_int)
#    # net-netsnmp_5.7.x knows data_size_p here as well but we ignore it for
#    # backwards compatibility with net-netsnmp_5.4.x.
#] 
#
#for f in [ netsnmp_netsnmp_create_watcher_info ]:
#    f.argtypes = [
#        ctypes.c_void_p,                # void *data
#        ctypes.c_size_t,                # size_t size
#        ctypes.c_ubyte,                 # u_char type
#        ctypes.c_int                    # int flags
#    ]
#    f.restype = netsnmp_watcher_info_p
#
#for f in [ netsnmp_netsnmp_register_watched_instance ]:
#    f.argtypes = [
#        netsnmp_handler_registration_p, # netsnmp_handler_registration *reginfo
#        netsnmp_watcher_info_p          # netsnmp_watcher_info *winfo
#    ]
#    f.restype = ctypes.c_int
#
#for f in [ netsnmp_netsnmp_register_watched_scalar ]:
#    f.argtypes = [
#        netsnmp_handler_registration_p, # netsnmp_handler_registration *reginfo
#        netsnmp_watcher_info_p          # netsnmp_watcher_info *winfo
#    ]
#    f.restype = ctypes.c_int


# include/net-netsnmp_agent/table_data.h
#class netsnmp_table_row(ctypes.Structure): pass
#netsnmp_table_row_p = ctypes.POINTER(netsnmp_table_row)
#netsnmp_table_row._fields_ = [
#    ("indexes",             netsnmp_variable_list_p),
#    ("index_oid",           c_oid_p),
#    ("index_oid_len",       ctypes.c_size_t),
#    ("data",                ctypes.c_void_p),
#    ("next",                netsnmp_table_row_p),
#    ("prev",                netsnmp_table_row_p)
#]
#
#class netsnmp_table_data(ctypes.Structure): pass
#netsnmp_table_data_p = ctypes.POINTER(netsnmp_table_data)
#netsnmp_table_data._fields_ = [
#    ("indexes_template",    netsnmp_variable_list_p),
#    ("name",                ctypes.c_char_p),
#    ("flags",               ctypes.c_int),
#    ("store_indexes",       ctypes.c_int),
#    ("first_row",           netsnmp_table_row_p),
#    ("last_row",            netsnmp_table_row_p)
#]
#
## include/net-netsnmp_agent/table_dataset.h
#class netsnmp_table_data_set_storage_udata(ctypes.Union): pass
#netsnmp_table_data_set_storage_udata._fields_ = [
#    ("voidp",               ctypes.c_void_p),
#    ("integer",             ctypes.POINTER(ctypes.c_long)),
#    ("string",              ctypes.c_char_p),
#    ("objid",               c_oid_p),
#    ("bitstring",           ctypes.POINTER(ctypes.c_ubyte)),
#    ("counter64",           ctypes.POINTER(counter64)),
#    ("floatVal",            ctypes.POINTER(ctypes.c_float)),
#    ("doubleVal",           ctypes.POINTER(ctypes.c_double))
#]
#
#class netsnmp_table_data_set_storage(ctypes.Structure): pass
#netsnmp_table_data_set_storage_p = ctypes.POINTER(netsnmp_table_data_set_storage)
#netsnmp_table_data_set_storage._fields_ = [
#    ("column",              ctypes.c_uint),
#    ("writable",            ctypes.c_byte),
#    ("change_ok_fn",        ctypes.c_void_p),
#    ("my_change_data",      ctypes.c_void_p),
#    ("type",                ctypes.c_ubyte),
#    ("data",                netsnmp_table_data_set_storage_udata),
#    ("data_len",            ctypes.c_ulong),
#    ("next",                netsnmp_table_data_set_storage_p)
#]
#
#class netsnmp_table_data_set(ctypes.Structure): pass
#netsnmp_table_data_set_p = ctypes.POINTER(netsnmp_table_data_set)
#netsnmp_table_data_set._fields_ = [
#    ("table",               netsnmp_table_data_p),
#    ("default_row",         netsnmp_table_data_set_storage_p),
#    ("allow_creation",      ctypes.c_int),
#    ("rowstatus_column",    ctypes.c_uint)
#]
#
#for f in [ netsnmp_netsnmp_create_table_data_set ]:
#    f.argtypes = [
#        ctypes.c_char_p                 # const char *table_name
#    ]
#    f.restype = netsnmp_table_data_set_p
#
#for f in [ netsnmp_netsnmp_table_dataset_add_row ]:
#    f.argtypes = [
#        netsnmp_table_data_set_p,       # netsnmp_table_data_set *table
#        netsnmp_table_row_p,            # netsnmp_table_row *row
#    ]
#    f.restype = None
#
#for f in [ netsnmp_netsnmp_table_data_set_create_row_from_defaults ]:
#    f.argtypes = [
#        netsnmp_table_data_set_storage_p # netsnmp_table_data_set_storage *defrow
#    ]
#    f.restype = netsnmp_table_row_p
#
#for f in [ netsnmp_netsnmp_table_set_add_default_row ]:
#    f.argtypes = [
#        netsnmp_table_data_set_p,       # netsnmp_table_data_set *table_set
#        ctypes.c_uint,                  # unsigned int column
#        ctypes.c_int,                   # int type
#        ctypes.c_int,                   # int writable
#        ctypes.c_void_p,                # void *default_value
#        ctypes.c_size_t                 # size_t default_value_len
#    ]
#    f.restype = ctypes.c_int
#
#for f in [ netsnmp_netsnmp_register_table_data_set ]:
#    f.argtypes = [
#        netsnmp_handler_registration_p, # netsnmp_handler_registration *reginfo
#        netsnmp_table_data_set_p,       # netsnmp_table_data_set *data_set
#        ctypes.c_void_p                 # netsnmp_table_registration_info *table_info
#    ]
#    f.restype = ctypes.c_int
#
#for f in [ netsnmp_netsnmp_set_row_column ]:
#    f.argtypes = [
#        netsnmp_table_row_p,            # netsnmp_table_row *row
#        ctypes.c_uint,                  # unsigned int column
#        ctypes.c_int,                   # int type
#        ctypes.c_void_p,                # const void *value
#        ctypes.c_size_t                 # size_t value_len
#    ]
#    f.restype = ctypes.c_int
#
#for f in [ netsnmp_netsnmp_table_dataset_add_index ]:
#    f.argtypes = [
#        netsnmp_table_data_set_p,       # netsnmp_table_data_set *table
#        ctypes.c_ubyte                  # u_char type
#    ]
#    f.restype = None
#
#for f in [ netsnmp_netsnmp_table_dataset_remove_and_delete_row ]:
#    f.argtypes = [
#        netsnmp_table_data_set_p,       # netsnmp_table_data_set *table
#        netsnmp_table_row_p             # netsnmp_table_row *row
#    ]
#
## include/net-netsnmp_agent/snmp_agent.h
#for f in [ netsnmp_agent_check_and_process ]:
#    f.argtypes = [
#        ctypes.c_int                    # int block
#    ]
#    f.restype = ctypes.c_int
#
#print(session)
#print(session._fields_)
#netsnmp_= ctypes.cdll.LoadLibrary(ctypes.util.find_library('netsnmp'))

for f in [ netsnmp.netsnmp_query_get ]:
    f.argtypes = [
        netsnmp_variable_list_p,
        netsnmp_session_p
    ]
    f.restype = ctypes.c_int

for f in [ netsnmp.snmp_set_do_debugging ]:
    f.argtypes = [
        ctypes.c_int
    ]
    f.restype = None

for f in [ netsnmp.snmp_errstring ]:
    f.restype = c_char_p

for f in [ netsnmp.netsnmp_get_version ]:
    f.restype = c_char_p

print('--', 1, '--')
name = ctypes.create_string_buffer(b'Test')
netsnmp.init_snmp(ctypes.cast(name, c_char_p))
netsnmp.snmp_set_do_debugging(1)

session = netsnmp_session()
session_ptr = ctypes.byref(session)

print('session  =', session)
print('&session =', session_ptr)

print('--', 2, '--')


netsnmp.snmp_log(LOG_ERR, b'TEST ERR MSG\n')


netsnmp.snmp_sess_init(ctypes.cast(session_ptr, netsnmp_session_p))
session.remote_port = 161
session.timeout = 100000
session.retries = 5
session.version = SNMP_VERSION_2c
session.securityModel = -1
session.rcvMsgMaxSize = 1472
session.flags |= 0x100
#session.peername = 'xfwars-po-01'.encode()
session.peername = b'127.0.0.1'
session.community = b'c0mcab113'
session.community_len = len(session.community)
print('session config done')

sess_handler = netsnmp.snmp_open(session_ptr)
print(sess_handler)

#print(ctypes.cast(session_ptr, netsnmp_session_p))
#sessp = netsnmp.snmp_sess_session(netsnmp.snmp_sess_open(ctypes.cast(session_ptr, netsnmp_session_p)))
#sessp = netsnmp.snmp_sess_session(ss)
#sessp_ptr = ctypes.byref(sessp)
#print('sessp    =', sessp)
#print('&sessp   =', sessp_ptr)
#print(netsnmp.snmp_close(sessp))

print('--', 3, '--')
pdu     = netsnmp.snmp_pdu_create(160)
pdu_ptr = ctypes.byref(pdu)
print('pdu      =', pdu)
print('&pdu     =', pdu_ptr)

oid     = (c_oid * MAX_OID_LEN)()
oid_ptr = ctypes.byref(oid)
print('oid      =', oid)
print('&oid     =', oid_ptr)

oidstr     = ctypes.create_string_buffer(b'.1.3.6.1.2.1.1.1.0')
#oidstr     = ctypes.create_string_buffer(b'sysDescr.0')
oidstr_ptr = ctypes.byref(oidstr)
print('oidstr   =', oidstr)
print('&oidstr  =', oidstr_ptr)

oidlen     = ctypes.c_size_t(MAX_OID_LEN)
oidlen_ptr = ctypes.byref(oidlen)
print('oidlen   =', oidlen)
print('&oidlen  =', oidlen_ptr)

for x in oid:
    print(x, end='')
print()
#ret = netsnmp.get_node(
ret = netsnmp.read_objid(
        ctypes.cast(oidstr, c_char_p),
        ctypes.cast(oid, c_oid_p),
        ctypes.cast(oidlen_ptr, POINTER(_size)))
for x in oid:
    print(x, end='')
print()
if not ret == 1:
    print('read_objid error')


vars = netsnmp.snmp_add_null_var(pdu, ctypes.cast(oid, c_oid_p), oidlen)
vars_ptr = ctypes.byref(vars)
print('vars     =', vars)
print('&vars    =', vars_ptr)

print('--', 5, '--')
print('Net-SNMP Version', netsnmp.netsnmp_get_version().decode())

#print(netsnmp.snmp_errno())
#ret = netsnmp.netsnmp_query_get(vars, session_ptr)
resp_ptr = netsnmp_pdu_p()
ret = netsnmp.snmp_synch_response(session_ptr, pdu, resp_ptr)
print(ret)

print(netsnmp.snmp_errstring().decode())
#netsnmp.snmp_shutdown(name)
netsnmp.snmp_log(LOG_ERR, b'END\n')

#ctypes.cdll.LoadLibrary('libdl.so').dlclose(netsnmp._handle)
