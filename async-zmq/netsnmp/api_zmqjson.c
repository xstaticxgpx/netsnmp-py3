#include <Python.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/types.h>
#include <net-snmp/library/large_fd_set.h>

#include <zmq.h>
#include <czmq.h>

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
int active_hosts = 0;

/* Global ZeroMQ pointers */
zctx_t *zmq_ctx;
void *zmq_push;

oid oid_root[] = { 1, 3, 6, 1, 2, 1 };

/* Definitions */
static long long __py_attr_long (PyObject *, char *);
static void *__py_attr_void_ptr (PyObject *, char *);
static int __py_attr_get_string (PyObject *, char *, char **, Py_ssize_t *);
static int __py_attr_set_string (PyObject *, char *, char *, size_t);

static PyObject *get_async      (PyObject *, PyObject *);

static netsnmp_callback *callback(int, netsnmp_session *, int, netsnmp_pdu *, void *);

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

static netsnmp_callback *
callback(int operation, netsnmp_session *ss, int reqid,
         netsnmp_pdu *pdu, void *magic)
{
    netsnmp_variable_list *vars;
    PyObject *_cb;
    PyObject *var_list;
    zmsg_t *zmqmsg = zmsg_new();
    size_t out_len = 0;
    int buf_over = 0;
    int len;
    char mib_buf[MAX_OID_LEN], *mib_bufp = mib_buf;
    size_t mib_buf_len = MAX_OID_LEN;
    char str_buf[STR_BUF_SIZE], *str_bufp = str_buf;
    size_t str_buf_len = STR_BUF_SIZE;

    _cb = (PyObject *)magic;
    pid_t proc_id = getpid();

    if (_debug_level) printf("### callback operation:%d\n", operation);
    if (_debug_level) printf("### callback reqid:%d\n", reqid);
    if (_debug_level) printf("### callback host:%s\n", ss->peername);

    zmsg_addstr(zmqmsg, "{\"host\":\"%s\",", ss->peername);
    if (operation == NETSNMP_CALLBACK_OP_RECEIVED_MESSAGE) {
        zmsg_addstr(zmqmsg, "\"op\":%d,\"vars\":{", operation);
        //var_list = PyList_New(0);
        for (vars = pdu->variables; vars; vars = vars->next_variable, out_len = 0) {

            // Get response OID
            netsnmp_sprint_realloc_objid(&mib_bufp, &mib_buf_len,
                                         &out_len, 1, &buf_over,
                                         vars->name, vars->name_length);
            // Get response text
            len = snprint_value(str_bufp, str_buf_len, vars->name, vars->name_length, vars);

            // Append Python tuple (type, oid, response) to list
            //PyList_Append(var_list, Py_BuildValue("(iss)", vars->type, mib_bufp, str_bufp));
            zmsg_addstr(zmqmsg, "\"%s\":\"%s\"%s", mib_bufp, str_bufp, vars->next_variable ? "," : "}");
        }
    } else
        zmsg_addstr(zmqmsg, "\"op\":%d", operation);
    zmsg_addstr(zmqmsg, "}");
    //PyObject_CallFunction(_cb, "iiisO", proc_id, operation, reqid, ss->peername, var_list ? var_list : Py_BuildValue("i", 0));
    //zstr_sendf(zmq_push, "{\"pid\":%d,\"op\":%d,\"host\":\"%s\"}", proc_id, operation, ss->peername);
    zmsg_send(&zmqmsg, zmq_push);
    active_hosts--;
    return 1;
}

static PyObject *
get_async(PyObject *self, PyObject *args) 
{
  PyObject *hosttuple;
  PyObject *host_iter;
  PyObject *host;
  PyObject *name;
  PyObject *comm;
  PyObject *oids;
  PyObject *oids_iter;
  netsnmp_variable_list *var;
  size_t oid_arr_len;
  oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
  int timeout;
  int retries;
  PyObject *py_callback;
  int fds = 0, block = 1;
  netsnmp_large_fd_set lfdset;
  pid_t proc_id = getpid();
  char *snmp_open_err;
  char *snmp_send_err;


    zmq_ctx = zctx_new();
    zmq_push = zsocket_new(zmq_ctx, ZMQ_PUSH);

    if ((zmq_connect(zmq_push, "tcp://localhost:1100")) < 0) {
        PyErr_Format(PyExc_RuntimeError, "get: unable to open zeromq socket\n");
        return;
    }

    if (!PyArg_ParseTuple(args, "OiiO", &hosttuple, &timeout, &retries, &py_callback)) {
        PyErr_Format(PyExc_RuntimeError, "get: unable to parse args tuple\n");
        return;
    }

    //ss = (netsnmp_session *)__py_attr_void_ptr(session, "sess_ptr");
    snmp_set_do_debugging(0);
    snmp_disable_stderrlog();
    snmp_set_quick_print(1);

    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DONT_PERSIST_STATE, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_LOAD, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_SAVE, 1);
    /*
    netsnmp_set_mib_directory("/usr/share/snmp/mibs");
    set_configuration_directory("/dev/null");
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_EXTENDED_INDEX, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_NUMERIC_TIMETICKS, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_BARE_VALUE, 1);
    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_HEX_TEXT, 1);
    */

    //init_snmp("testasync");

    /*
     * a list of variables to query for
    struct oid {
      const char *Name;
      oid Oid[MAX_OID_LEN];
      int OidLen;
    } oids[] = {
      { "1.3.6.1.2.1.1.1.0" },
      { NULL }
    };
     */

    if (_debug_level) printf("### %d starting session\n", proc_id);

    // Initiate session early in order to parse OIDs below (read_objid)
    //snmp_sess_init(&ss);
    host_iter = PyObject_GetIter(hosttuple);

    while (host_iter && (host = PyIter_Next(host_iter))) {

      netsnmp_pdu *req;
      netsnmp_session sess, *ss;

      if(!(PyTuple_Check(host))) {
        PyErr_Format(PyExc_RuntimeError, "get: unable to parse host tuple\n");
        return;
      }
      name = PyUnicode_AsUTF8(PyTuple_GetItem(host, 0));
      comm = PyUnicode_AsUTF8(PyTuple_GetItem(host, 1));
      oids = PyTuple_GetItem(host, 2);
      asprintf(&snmp_open_err, "[%d] snmp_open %s", proc_id, name);
      asprintf(&snmp_send_err, "[%d] snmp_send %s", proc_id, name);

      snmp_sess_init(&sess);

      req = snmp_pdu_create(SNMP_MSG_GET);    /* build PDU */
      for ((oids_iter = PyObject_GetIter(oids)); (var = PyIter_Next(oids_iter)); (oid_arr_len = MAX_OID_LEN)) {
          snmp_parse_oid(PyUnicode_AsUTF8((PyObject *)var), oid_arr_ptr, &oid_arr_len);
          snmp_add_null_var(req, oid_arr_ptr, oid_arr_len);
          Py_DECREF(var);
      }
      Py_DECREF(oids_iter);

      sess.version       = SNMP_VERSION_2c;
      sess.peername      = name;
      sess.timeout       = timeout*1000;
      sess.retries       = retries;
      sess.community     = comm;
      sess.community_len = strlen(sess.community);
      sess.callback      = callback;
      sess.callback_magic= (void *)py_callback;

      if (!(ss = snmp_open(&sess))) {
        snmp_perror(snmp_open_err);
        continue;
      }
      if (snmp_send(ss, req)) {
        if (_debug_level) printf("### %d sent request to %s\n", proc_id, ss->peername);
        active_hosts++;
      } else {
        // try again
        //if (!(snmp_send(ss, req))) {
        snmp_perror(snmp_send_err);
        snmp_free_pdu(req);
        //} else active_hosts++;
      }
      Py_DECREF(host);
    }
    Py_DECREF(host_iter);
    
    if (_debug_level) printf("### %d starting fd poll\n", proc_id);
    netsnmp_large_fd_set_init(&lfdset, fds);
    while (active_hosts) {
      fds = 0, block = 1;
      struct timeval timeout;
  
      //snmp_select_info(&fds, &fdset, &timeout, &block);
      snmp_select_info2(&fds, &lfdset, &timeout, &block);
      if (_debug_level) printf("### %d polling %d FDs\n", proc_id, fds);
      //fds = select(fds, &fdset, NULL, NULL, block ? NULL : &timeout);
      //fds = select(fds, (&lfdset)->lfs_setptr, NULL, NULL, block ? NULL : &timeout);
      fds = netsnmp_large_fd_set_select(fds, &lfdset, NULL, NULL, block ? NULL : &timeout);
  
      if (fds < 0) {
          PyErr_Format(PyExc_RuntimeError, "get: select failed\n");
          return;
      }

      if (_debug_level) printf("### %d polled %d FDs\n", proc_id, fds);
  
      if (fds) {
          //snmp_read(&fdset);
          snmp_read2(&lfdset);
      } else {
          snmp_timeout();
      }
    }

    //zstr_sendf(zmq_push, "\{\"pid\":%d,\"op\":\"completed\"}", proc_id);
    zsocket_destroy(zmq_ctx, zmq_push);
    snmp_close_sessions();
    return Py_BuildValue("i", 1);
}

/* Define python interface */

static PyMethodDef APIMethods[] = {
    {"get_async", get_async, METH_VARARGS,
     "asynchronous snmp get request"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef API = {
    PyModuleDef_HEAD_INIT,
    "netsnmp",           /* m_name */
    "NET-SNMP API",      /* m_doc */
    -1,                  /* m_size */
    APIMethods,          /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
};

PyMODINIT_FUNC
PyInit_api(void)
{
    return PyModule_Create(&API);
}
