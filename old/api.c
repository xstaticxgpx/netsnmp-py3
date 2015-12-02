#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <ctype.h>
#ifdef I_SYS_TIME
#include <sys/time.h>
#endif
#include <netdb.h>
#include <stdlib.h>

#ifdef HAVE_REGEX_H
#include <regex.h>
#endif

#define SUCCESS 1
#define FAILURE 0

#define VARBIND_TAG_F 0
#define VARBIND_IID_F 1
#define VARBIND_VAL_F 2
#define VARBIND_TYPE_F 3

#define TYPE_UNKNOWN 0
#define MAX_TYPE_NAME_LEN 32
//MAX_OID_LEN = 128
#define STR_BUF_SIZE (MAX_TYPE_NAME_LEN * MAX_OID_LEN)
#define ENG_ID_BUF_SIZE 32

#define NO_RETRY_NOSUCH 0

#define USE_BASIC 0
#define USE_ENUMS 1
#define USE_SPRINT_VALUE 2

#define USE_NUMERIC_OIDS 0x08
#define NON_LEAF_NAME 0x04
#define USE_LONG_NAMES 0x02
#define FAIL_ON_NULL_IID 0x01
#define NO_FLAGS 0x00

/* Global Variables */
int _debug_level = 0;
oid oid_root[] = { 1, 3, 6, 1, 2, 1 };

/* Functions */

static long long
__py_attr_long(PyObject *obj, char * attr_name)
{
  long long val = -1;
  if (obj && attr_name  && PyObject_HasAttrString(obj, attr_name)) {
    PyObject *attr = PyObject_GetAttrString(obj, attr_name);
    if (attr) {
      val = PyLong_AsLongLong(attr);
      Py_DECREF(attr);
    }
  }
  return val;
}

static void *
__py_attr_void_ptr(PyObject *obj, char * attr_name)
{
  void *val = NULL;

  if (obj && attr_name  && PyObject_HasAttrString(obj, attr_name)) {
    PyObject *attr = PyObject_GetAttrString(obj, attr_name);
    if (attr) {
      val = PyLong_AsVoidPtr(attr);
      Py_DECREF(attr);
    }
  }
  return val;
}

static int
__py_attr_get_string(PyObject *obj, char * attr_name, char **val,
    Py_ssize_t *len)
{
  //printf("%s\n", "test-start");
  *val = NULL;
  int ret = -1;
  if (obj && attr_name && PyObject_HasAttrString(obj, attr_name)) {
    PyObject *attr = PyObject_GetAttrString(obj, attr_name);
    if (attr) {
      //printf("%s\n", "test-if");
      *val = (char *)PyUnicode_AsUTF8AndSize(attr, len);
      Py_DECREF(attr);
      ret++;
    }
  }
  //printf("%s\n", "test-return");
  return ret;
}

static int
__py_attr_set_string(PyObject *obj, char *attr_name,
               char *val, size_t len)
{
  int ret = -1;
  if (obj && attr_name) {
    PyObject* val_obj = (val ?
              Py_BuildValue("s", val) :
              Py_BuildValue(""));
    ret = PyObject_SetAttrString(obj, attr_name, val_obj);
    Py_DECREF(val_obj);
  }
  return ret;
}

static int
__get_type_str (int type, char *str)
{
   switch (type) {
    case ASN_BOOLEAN:
            strcpy(str, "BOOLEAN");
            break;
    case ASN_INTEGER:
            strcpy(str, "INTEGER");
            break;
    case ASN_BIT_STR:
            strcpy(str, "BITSTR");
            break;
    case ASN_OCTET_STR:
            strcpy(str, "STRING");
            break;
    case ASN_NULL:
            strcpy(str, "NULL");
            break;
    case ASN_OBJECT_ID:
            strcpy(str, "OID");
            break;
    case ASN_SEQUENCE:
            strcpy(str, "SEQUENCE");
            break;
    case ASN_SET:
            strcpy(str, "SET");
            break;
    case ASN_TIMETICKS:
            strcpy(str, "Timeticks");
            break;
    case ASN_COUNTER:
            strcpy(str, "Counter32");
            break;
    case ASN_OPAQUE:
            strcpy(str, "Opaque");
            break;
    case ASN_COUNTER64:
            strcpy(str, "Counter64");
            break;
    case ASN_INTEGER64:
            strcpy(str, "Integer64");
            break;
    case ASN_GAUGE:
            strcpy(str, "Gauge32");
            break;
    case ASN_IPADDRESS:
            strcpy(str, "IpAddress");
            break;
    case SNMP_ENDOFMIBVIEW:
            strcpy(str, "ENDOFMIBVIEW");
            break;
    case SNMP_NOSUCHOBJECT:
            strcpy(str, "NOSUCHOBJECT");
            break;
    case SNMP_NOSUCHINSTANCE:
            strcpy(str, "NOSUCHINSTANCE");
            break;
    default: /* unconfigured types for now */
            strcpy(str, "UNKNOWN");
            if (_debug_level) printf("__get_type_str:FAILURE(%d)\n", type);
   }
   return SUCCESS;
}


static PyObject *
create_session(PyObject *self, PyObject *args)
{
  int version;
  int retries;
  int timeout;
  char *peer;
  const char *community;
  netsnmp_session session, *ss;

    if (!PyArg_ParseTuple(args, "iiissi", &version, &timeout,
                		  &retries, &community, &peer, &_debug_level)) {
        PyErr_Format(SNMPError, "session: unable to parse tuple");
        return;
    }

    snmp_set_do_debugging(_debug_level);
    snmp_disable_stderrlog();
    snmp_set_quick_print(1);
    set_configuration_directory("/dev/null");
    netsnmp_set_mib_directory("/dev/null");

    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DONT_PERSIST_STATE, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_LOAD, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_SAVE, 1);
    /*
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_EXTENDED_INDEX, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_NUMERIC_TIMETICKS, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_BARE_VALUE, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_HEX_TEXT, 1);
    */

    snmp_sess_init(&session);

    session.version = version;
    session.retries = retries;
    session.timeout = timeout;
    session.peername = peer;
    session.community = community;
    session.community_len = strlen(community);

    ss = snmp_sess_open(&session);
    if (ss == NULL) {
        PyErr_Format(SNMPError, "Couldn't open SNMP session\n");
        return;
    }
    return PyLong_FromVoidPtr((void *)ss);
}

static PyObject *
close_session(PyObject *self, PyObject *args)
{
  PyObject *session;
  netsnmp_session *ss;

    if (!PyArg_ParseTuple(args, "O", &session)) {
        PyErr_Format(SNMPError, "close_session: unable to parse tuple");
        return;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");
    snmp_sess_close(ss);

    return Py_BuildValue("i", 1);
}

static PyObject *
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
        snmp_sess_close(ss);
        PyErr_Format(SNMPError, "get: unable to parse tuple\n");
        return;
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
                return;
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
        return;
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
                netsnmp_sprint_realloc_objid(&mib_bufp, &mib_buf_len,
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
                    return;
                } else {
                    __py_attr_set_string(varbind, "response", str_buf, len);

                    __get_type_str(var->type, type_str);
                    __py_attr_set_string(varbind, "type", type_str, strlen(type_str));

                    __py_attr_set_string(varbind, "oid", mib_buf, mib_buf_len);
                }
        }
        snmp_free_pdu(response);
        //snmp_sess_close(ss);
    }
    return Py_BuildValue("i", 1);
}

static PyObject *
getnext(PyObject *self, PyObject *args) 
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
    oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
    size_t oid_arr_len = MAX_OID_LEN;
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
        snmp_sess_close(ss);
        PyErr_Format(SNMPError, "getnext: unable to parse tuple\n");
        return;
    }

    ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");

    pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);

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
                PyErr_Format(SNMPError, "getnext: unknown object ID (%s)\n", (request ? request : "<null>"));
                return;
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

    if (response == NULL && (status == STAT_SUCCESS)) {
        status = STAT_ERROR;
    }

    if (!status == STAT_SUCCESS) {
        snmp_sess_error(ss, &err_num, &snmp_err_num, &err_bufp);
        if (_debug_level) printf("snmp_syserr: %d\nsnmp_errnum: %d\n", err_num, -snmp_err_num);
        snmp_free_pdu(response);
        snmp_sess_close(ss);
        PyErr_Format(SNMPError, "%s\n", err_bufp);
        return;
    } else {
        /* initialize return tuple:
        res_tuple = PyTuple_New(varlist_len);
        for (varlist_ind = 0; varlist_ind < varlist_len; varlist_ind++) {
            PyTuple_SetItem(res_tuple, varlist_ind, Py_BuildValue(""));
        }
        */

        for(var = response->variables, varlist_ind = 0;
            var && (varlist_ind < varlist_len);
            var = var->next_variable, varlist_ind++, out_len = 0) {
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
                netsnmp_sprint_realloc_objid(&mib_bufp, &mib_buf_len,
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
                    PyErr_Format(SNMPError, "getnext: null response (%s)\n",  mib_buf);
                    return;
                } else {
                    __py_attr_set_string(varbind, "response", str_buf, len);

                    __get_type_str(var->type, type_str);
                    __py_attr_set_string(varbind, "type", type_str, strlen(type_str));

                    __py_attr_set_string(varbind, "oid", mib_buf, mib_buf_len);
                }
        }
        snmp_free_pdu(response);
        //snmp_sess_close(ss);
    }
    return Py_BuildValue("i", 1);
}

static PyObject *
walk(PyObject *self, PyObject *args) 
{
    PyObject *session;
    PyObject *varlist;
    PyObject *varlist_iter;
    PyObject *varbind;
    PyObject *nullvar;
    netsnmp_session *ss;
    char *request;
    netsnmp_pdu *pdu, *response;
    netsnmp_variable_list *var;
    int varindx;
    int varlist_ind;
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
        snmp_sess_close(ss);
        PyErr_Format(SNMPError, "walk: unable to parse tuple\n");
        return;
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
                        return;
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
                                netsnmp_sprint_realloc_objid(&mib_bufp, &mib_buf_len,
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
                                    return;
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
                return;
            }
        }
    }

    //snmp_sess_close(ss);
    return Py_BuildValue("i", 1);
}

/* Define python interface

static PyMethodDef APIMethods[] = {
    {"create_session",  create_session, METH_VARARGS,
     "create netsnmp session"},
    {"get", get, METH_VARARGS,
     "snmp get request"},
    {"getnext", getnext, METH_VARARGS,
     "snmp getnext request"},
    {"walk", walk, METH_VARARGS,
     "snmp walk request"},
    {"close_session",  close_session, METH_VARARGS,
     "close netsnmp session"},
    {NULL, NULL, 0, NULL}       
};

static struct PyModuleDef API = {
    PyModuleDef_HEAD_INIT,
    "netsnmp.api",       // m_name
    "NET-SNMP API",      // m_doc
    -1,                  // m_size
    APIMethods,          // m_methods
    NULL,                // m_reload
    NULL,                // m_traverse
    NULL,                // m_clear
    NULL,                // m_free
};

PyMODINIT_FUNC
PyInit_api(void)
{
    PyObject *m;

    m = PyModule_Create(&API);
    if (m == NULL)
        return;

    // Define SNMPError exception
    SNMPError = PyErr_NewException("netsnmp.api.SNMPError", NULL, NULL);
    Py_INCREF(SNMPError);
    PyModule_AddObject(m, "SNMPError", SNMPError);

    return m;
} */
