#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/net-snmp-features.h>


PyObject *
create_session(PyObject *self, PyObject *args)
{
  int version;
  int retries;
  int timeout;
  char *peer;
  char *community;
  netsnmp_session session, *ss;

    if (!PyArg_ParseTuple(args, "iiissi", &version, &timeout,
                          &retries, &community, &peer, &_debug_level)) {
        PyErr_Format(SNMPError, "session: unable to parse tuple");
        return NULL;
    }

    snmp_set_do_debugging(_debug_level==2 ? 1 : 0);
    snmp_disable_stderrlog();
    snmp_set_quick_print(1);
    set_configuration_directory("/dev/null");
    netsnmp_set_mib_directory("/dev/null");

    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DONT_PERSIST_STATE, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_LOAD, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_SAVE, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_BARE_VALUE, 1);
    //
    /*
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_EXTENDED_INDEX, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_NUMERIC_TIMETICKS, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_HEX_TEXT, 1);
    netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_STRING_OUTPUT_FORMAT, NETSNMP_STRING_OUTPUT_ASCII);
    */

    snmp_sess_init(&session);

    session.version = version;
    session.retries = retries;
    session.timeout = timeout;
    session.peername = peer;
    session.community = (u_char *)community;
    session.community_len = strlen(community);

    ss = snmp_sess_open(&session);
    if (ss == NULL) {
        PyErr_Format(SNMPError, "Couldn't open SNMP session\n");
        return NULL;
    }
    if (_debug_level) printf("### created session at %p\n", ss);
    return PyLong_FromVoidPtr((void *)ss);
}

PyObject *
close_session(PyObject *self, PyObject *args)
{
  PyObject *session;
  netsnmp_session *ss;

    if (!PyArg_ParseTuple(args, "O", &session)) {
        PyErr_Format(SNMPError, "close_session: unable to parse tuple");
        return NULL;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");
    if (_debug_level) printf("### closing session at %p\n", ss);
    snmp_sess_close(ss);

    return Py_BuildValue("i", SUCCESS);
}
