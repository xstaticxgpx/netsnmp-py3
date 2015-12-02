#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

PyObject *
get(PyObject *self, PyObject *args) 
{
  PyObject *session;
  PyObject *varlist;
  PyObject *varlist_iter;
  PyObject *varbind;
  netsnmp_session *ss;
  char *request;
  netsnmp_pdu *pdu, *response;
  netsnmp_variable_list *var;
  int varlist_len = 0;
  int varlist_ind;
  size_t oid_arr_len;
  oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
  char type_str[MAX_TYPE_NAME_LEN];
  char mib_buf[MAX_OID_LEN], *mib_bufp = mib_buf;
  size_t mib_buf_len = MAX_OID_LEN;
  char str_buf[STR_BUF_SIZE], *str_bufp = str_buf;
  size_t str_buf_len = STR_BUF_SIZE;
  size_t out_len = 0;
  int buf_over = 0;
  int status;
  int len;
  int err_num;
  int snmp_err_num;
  char err_buf[STR_BUF_SIZE], *err_bufp = err_buf;

    if (!PyArg_ParseTuple(args, "OO", &session, &varlist)) {
        //snmp_sess_close(ss);
        PyErr_Format(SNMPError, "get: unable to parse tuple\n");
        return NULL;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");

    pdu = snmp_pdu_create(SNMP_MSG_GET);

    if (varlist) {

        varlist_iter = PyObject_GetIter(varlist);

        while (varlist_iter && (varbind = PyIter_Next(varlist_iter)) && (oid_arr_len = MAX_OID_LEN)) {
            if (__py_attr_get_string(varbind, "request", &request, NULL) < 0)
            {
                oid_arr_len = 0;
            } else {

                if (!snmp_parse_oid(request, oid_arr_ptr, &oid_arr_len)) {
                   oid_arr_len = 0;
                }
            }

            if (oid_arr_len) {
                snmp_add_null_var(pdu, oid_arr_ptr, oid_arr_len);
                varlist_len++;
            } else {
                snmp_free_pdu(pdu);
                snmp_sess_close(ss);
                PyErr_Format(SNMPError, "get: unknown object ID (%s)\n", (request ? request : "<null>"));
                return NULL;
            }
            Py_DECREF(varbind);
        }
        Py_DECREF(varlist_iter);
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
        snmp_sess_close(ss);
        PyErr_Format(SNMPError, "%s\n", err_bufp);
        return NULL;
    } else {
        /* initialize return tuple:
        res_tuple = PyTuple_New(varlist_len);
        for (varlist_ind = 0; varlist_ind < varlist_len; varlist_ind++) {
            PyTuple_SetItem(res_tuple, varlist_ind, Py_BuildValue(""));
        }
        */

        for(var = response->variables, varlist_ind = 0;
            var && (varlist_ind < varlist_len);
            var = var->next_variable, varlist_ind++, out_len = 0 ) {
                /* netsnmp library stdout print call:
                print_variable(var->name, var->name_length, var);
                */
                
                varbind = PySequence_GetItem(varlist, varlist_ind);

                /*
                 * void
                 * netsnmp_sprint_realloc_objid(u_char ** buf, size_t * buf_len,
                 *                              size_t * out_len, int allow_realloc,
                 *                              int *buf_overflow,
                 *                              const oid * objid, size_t objidlen)
                 */
                //printf("%p\n", mib_bufp);
                //printf("%d\n", out_len);
                //TODO??
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
                    snmp_sess_close(ss);
                    PyErr_Format(SNMPError, "get: null response (%s)\n", mib_buf);
                    return NULL;
                } else {
                    __py_attr_set_string(varbind, "response", str_buf, len);

                    __get_type_str(var->type, type_str);
                    __py_attr_set_string(varbind, "typestr", type_str, strlen(type_str));

                    __py_attr_set_string(varbind, "oid", mib_buf, mib_buf_len);
                }
        }
        snmp_free_pdu(response);
        //snmp_sess_close(ss);
    }
    return Py_BuildValue("i", 1);
}
