#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

/*
 *
 * This function should set one value at time.
 * Maybe it would be better this way.
 *
 */
PyObject *
set(PyObject *self, PyObject *args) 
{
  PyObject *session;
  netsnmp_session *ss;
  netsnmp_pdu *pdu, *response;
  size_t oid_arr_len = MAX_OID_LEN;
  oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
  int status;
  int err_num;
  int snmp_err_num;
  char err_buf[SPRINT_MAX_LEN], *err_bufp = err_buf;
  char *value, *value_type, *oids;

    // These arguments has been simplified - only accepts in the format we already need to use in the SNMP API
    // So who pass them along has to take care of the little tricks, specially with value_type.
    //if (!PyArg_ParseTuple(args, "OsOss", &session, &oids, &responses, &value_type, &value)) {
    if (!PyArg_ParseTuple(args, "Osss", &session, &oids, &value_type, &value)) {
        //snmp_sess_close(ss);
        PyErr_Format(SNMPError, "set: unable to parse arguments\n");
        return NULL;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");
    pdu = snmp_pdu_create(SNMP_MSG_SET);
    if (!pdu) {
        PyErr_Format(SNMPError, "set: could not create PDU\n");
        return NULL;
    }
    
    if (oids) {
        //int ret = 0;
        char type = value_type[0];
        // basic checks. Let the complicated part in the python code
        switch (type) {
        case 'i': case 'u': case 't':
        case 'a': case 'o': case 's':
        case 'x': case 'd': case 'n':
        case 'U': case 'I': case 'F':
        case 'D':
            break;
        default:
            PyErr_Format(SNMPError, "set: error with value type (type is invalid or unknow)\n");
            return NULL;
        }
    
        if (snmp_parse_oid(oids, oid_arr_ptr, &oid_arr_len)) {
            snmp_add_var(pdu, oid_arr_ptr, oid_arr_len, type, value);
        } else {
            PyErr_Format(SNMPError, "set: unknown object ID for oid (%s)\n", (oids ? oids : "<null>"));
            return NULL;
        }
    } else {
        // Nothing here. We should return instead going through everything else.
        PyErr_Format(SNMPError, "set: error parsing oids argument (oids is null)\n");
        return NULL;
    }

    /*
     * int
     * snmp_sess_synch_response(void *sessp,
     *                          netsnmp_pdu *pdu, netsnmp_pdu **response)
     */
    // Macro to release the Python GIL during blocking I/O
    //Py_BEGIN_ALLOW_THREADS
    status = snmp_sess_synch_response(ss, pdu, &response);
    // Re-lock afterwards
    //Py_END_ALLOW_THREADS

    if (response == NULL && (status == STAT_SUCCESS))
        status = STAT_ERROR;

    if (status != STAT_SUCCESS) {
        snmp_sess_error(ss, &err_num, &snmp_err_num, &err_bufp);
        if (_debug_level) printf("snmp_syserr: %d\nsnmp_errnum: %d\n", err_num, -snmp_err_num);
        snmp_free_pdu(response);
        //snmp_sess_close(ss);
        PyErr_Format(SNMPError, "%s\n", err_bufp);
        return NULL;
    } 
    if (response)
        snmp_free_pdu(response);
    return Py_BuildValue("i", SUCCESS);
}
