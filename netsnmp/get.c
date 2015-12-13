#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

PyObject *
get(PyObject *self, PyObject *args) 
{
  PyObject *session;
  PyObject *oids;
  PyObject *oids_iter;
  PyObject *responses;
  PyObject *oidstr;
  PyObject *next;
  netsnmp_session *ss;
  netsnmp_pdu *pdu, *response;
  netsnmp_variable_list *var;
  size_t oid_arr_len;
  oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
  char mib_buf[MAX_OID_LEN], *mib_bufp = mib_buf;
  size_t mib_buf_len = -1;
  char str_buf[SPRINT_MAX_LEN], *str_bufp = str_buf;
  size_t str_buf_len = SPRINT_MAX_LEN;
  size_t out_len = 0;
  int buf_over = 0;
  int status;
  int len;
  int err_num;
  int snmp_err_num;
  char err_buf[SPRINT_MAX_LEN], *err_bufp = err_buf;
  Py_ssize_t *oidstr_len = 0;

    if (!PyArg_ParseTuple(args, "OOO", &session, &oids, &responses)) {
        //snmp_sess_close(ss);
        PyErr_Format(SNMPError, "get: unable to parse argument tuple\n");
        return NULL;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");

    next = PyObject_GetAttrString(session, "_next");
    if (next == Py_True) {
        pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);
    } else {
        pdu = snmp_pdu_create(SNMP_MSG_GET);
    }

    if (oids) {

        oids_iter = PyObject_GetIter(oids);

        while (oids_iter && (oidstr = PyIter_Next(oids_iter)) && (oid_arr_len = MAX_OID_LEN)) {

            char *_oidstr = (char *)PyUnicode_AsUTF8AndSize(oidstr, oidstr_len);
            if (!snmp_parse_oid(_oidstr, oid_arr_ptr, &oid_arr_len)) {
               oid_arr_len = 0;
            }

            if (oid_arr_len) {
                snmp_add_null_var(pdu, oid_arr_ptr, oid_arr_len);
            } else {
                snmp_free_pdu(pdu);
                //snmp_sess_close(ss);
                PyErr_Format(SNMPError, "get: unknown object ID (%s)\n", (_oidstr ? _oidstr : "<null>"));
                return NULL;
            }
            //Py_DECREF(_oidstr);
            Py_DECREF(oidstr);
        }
        Py_DECREF(oids_iter);
    }

    /*
     * int
     * snmp_sess_synch_response(void *sessp,
     *                          netsnmp_pdu *pdu, netsnmp_pdu **response)
     */
    // Macro to release the Python GIL during blocking I/O
    Py_BEGIN_ALLOW_THREADS
    status = snmp_sess_synch_response(ss, pdu, &response);
    // Re-lock afterwards
    Py_END_ALLOW_THREADS

    if (response == NULL && (status == STAT_SUCCESS))
        status = STAT_ERROR;

    if (!status == STAT_SUCCESS) {
        snmp_sess_error(ss, &err_num, &snmp_err_num, &err_bufp);
        if (_debug_level) printf("snmp_syserr: %d\nsnmp_errnum: %d\n", err_num, -snmp_err_num);
        snmp_free_pdu(response);
        //snmp_sess_close(ss);
        PyErr_Format(SNMPError, "%s\n", err_bufp);
        return NULL;
    } else {
        /* initialize return tuple:
        for (oids_ind = 0; oids_ind < oids_len; oids_ind++) {
            PyTuple_SetItem(res_tuple, oids_ind, Py_BuildValue(""));
        }
        */

        for(var = response->variables; var; var = var->next_variable, out_len = 0) {
                /* netsnmp library stdout print call:
                print_variable(var->name, var->name_length, var);
                */
                
                //varbind = PySequence_GetItem(oids, oids_ind);
                //PyObject *res_tuple = PyTuple_New(3);

                /*
                 * void
                 * netsnmp_sprint_realloc_objid(u_char ** buf, size_t * buf_len,
                 *                              size_t * out_len, int allow_realloc,
                 *                              int *buf_overflow,
                 *                              const oid * objid, size_t objidlen)
                 */
                //printf("%p\n", mib_bufp);
                //printf("%d\n", out_len);
                netsnmp_sprint_realloc_objid((u_char **)&mib_bufp, &mib_buf_len,
                                             &out_len, 1, &buf_over,
                                             var->name, var->name_length);

                /*
                 * int
                 * snprint_value(char *buf, size_t buf_len,
                 *               const oid * objid, size_t objidlen,
                 *               const netsnmp_variable_list * variable);
                 */
                len = snprint_value(str_bufp, str_buf_len, var->name, var->name_length, var);


                if (!(len > 0)) {
                    snmp_free_pdu(response);
                    //snmp_sess_close(ss);
                    PyErr_Format(SNMPError, "get: null response (%s)\n", mib_buf);
                    return NULL;
                } else {
                    /* old attribute methodology:
                    __py_attr_set_string(varbind, "response", str_buf, len);
                    __py_attr_set_string(varbind, "typestr", type_str, strlen(type_str));
                    __py_attr_set_string(varbind, "oid", mib_buf, mib_buf_len);
                    */

                    PyList_Append(responses, Py_BuildValue("(sss)", mib_buf, __get_type_str(var->type), str_buf));
                }
        }
        snmp_free_pdu(response);
        //snmp_sess_close(ss);
    }
    //return responses ? responses : NULL;
    return Py_BuildValue("i", 1);
}
