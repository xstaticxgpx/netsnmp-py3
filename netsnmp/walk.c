#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

PyObject *
walk(PyObject *self, PyObject *args) 
{
    PyObject *session;
    PyObject *varlist;
    PyObject *varbind;
    PyObject *nullvar;
    netsnmp_session *ss;
    char *request;
    netsnmp_pdu *pdu, *response;
    netsnmp_variable_list *var;
    int varindx;
    int varlist_len = 0;
    int varlist_request_len;
    oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
    size_t oid_arr_len = MAX_OID_LEN;
    oid end_oid[MAX_OID_LEN];
    size_t end_oid_len = 0;
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
    int request_index = 0;
    int responseiter;
    int requestiter;
    int running;

    if (!PyArg_ParseTuple(args, "OO", &session, &varlist)) {
        //snmp_sess_close(ss);
        PyErr_Format(SNMPError, "walk: unable to parse tuple\n");
        return NULL;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");

    if (varlist) {

        varlist_request_len   = PyList_Size(varlist);
        requestiter = 1;

        while ((requestiter <= varlist_request_len) && 
               (varbind = PyList_GetItem(varlist, request_index)) &&
               (oid_arr_len = MAX_OID_LEN)) {
            if (__py_attr_get_string(varbind, "request", &request, NULL) < 0)
            {
                oid_arr_len = 0;
            } else {
                if (!snmp_parse_oid(request, oid_arr_ptr, &oid_arr_len)) {
                    oid_arr_len = 0;
                } else {
                    running = 1;
                }
            }

            if (oid_arr_len) {

                // Configure end_oid as next sibling
                end_oid_len = oid_arr_len;
                memmove(end_oid, oid_arr, MAX_OID_LEN);
                end_oid[oid_arr_len-1]++;

                /* debugging:
                int i;
                printf("start: ");
                for(i=0;i<=oid_arr_len-1;i++) printf(".%d", oid_arr[i]);
                printf("\n");
                printf("end:   ");
                for(i=0;i<=oid_arr_len-1;i++) printf(".%d", end_oid[i]);
                printf("\n");*/
            
                responseiter = 0;
                while (running) {
                    varlist_len = PyList_Size(varlist);
            
                    pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);
                    snmp_add_null_var(pdu, oid_arr_ptr, oid_arr_len);
            
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
                
                    if (response == NULL && (status == STAT_SUCCESS)) {
                        status = STAT_ERROR;
                    }
                
                    if (!status == STAT_SUCCESS) {
                        snmp_sess_error(ss, &err_num, &snmp_err_num, &err_bufp);
                        if (_debug_level) printf("snmp_syserr: %d\nsnmp_errnum: %d\n", err_num, -snmp_err_num);
                        snmp_free_pdu(response);
                        snmp_sess_close(ss);
                        PyErr_Format(SNMPError, "%s\n", err_bufp);
                        return NULL;
                    } else {
                        for(var = response->variables; var;
                            var = var->next_variable, out_len = 0) {
                                /*
                                 * int
                                 * snmp_oid_compare(const oid * in_name1,
                                 *                  size_t len1, const oid * in_name2, size_t len2)
                                 *
                                 * @return -1 if name1 < name2, 0 if name1 = name2, 1 if name1 > name2
                                 */
                                if (snmp_oid_compare(end_oid, end_oid_len, var->name, var->name_length) <= 0) {
                                    if (responseiter == 0) {
                                        // if the first response is next sibling, set NOSUCHINSTANCE
                                        __get_type_str(SNMP_NOSUCHINSTANCE, type_str);
                                        __py_attr_set_string(varbind, "type", type_str, strlen(type_str));
                                    }
                                    //stop walking
                                    running = 0;
                                    break;
                                } else {
                                    if (responseiter > 0) {
                                        nullvar = PyObject_CallMethod(session, "nullvar", NULL);
                                        varindx = (varlist_len-varlist_request_len)+requestiter;
                                        PyList_Insert(varlist, varindx, nullvar);
                                        varlist_len++;
                                        varbind = PySequence_GetItem(varlist, varindx);
                                    } 
            
                                    //printf("%p\n", varbind);
                                }
            
                                // Setup for getnext on current response
                                memmove(oid_arr, var->name, var->name_length * sizeof(oid));
                                oid_arr_len = var->name_length;
                
                                /*
                                 * void
                                 * netsnmp_sprint_realloc_objid(u_char ** buf, size_t * buf_len,
                                 *                              size_t * out_len, int allow_realloc,
                                 *                              int *buf_overflow,
                                 *                              const oid * objid, size_t objidlen)
                                 */
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
                                    PyErr_Format(SNMPError, "walk: null response (%s)\n",  mib_buf);
                                    return NULL;
                                } else {
                                    __py_attr_set_string(varbind, "response", str_buf, len);
                
                                    __get_type_str(var->type, type_str);
                                    __py_attr_set_string(varbind, "type", type_str, strlen(type_str));
                
                                    __py_attr_set_string(varbind, "oid", mib_buf, mib_buf_len);
                                }
                        }
                        snmp_free_pdu(response);
                        responseiter++;
                    }
                }
                // Setup for next request
                request_index = (varlist_len-varlist_request_len)+requestiter;
                /* debugging:
                printf("end varlist_len = %d\n", varlist_len);
                printf("end request_index = %d\n", request_index);*/
                requestiter++;
            } else {
                snmp_sess_close(ss);
                PyErr_Format(SNMPError, "walk: unknown object ID (%s)\n", (request ? request : "<null>"));
                return NULL;
            }
        }
    }
    //snmp_sess_close(ss);
    return Py_BuildValue("i", 1);
}
