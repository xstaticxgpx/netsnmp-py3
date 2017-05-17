#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <net-snmp/library/large_fd_set.h>

#include <zmq.h>
#include <czmq.h>

#if CZMQ_VERSION_MAJOR < 3
#define zmsg_addstrf zmsg_addstr
#endif

/* Global counters */
static int active_hosts = 0;
/* Global ZeroMQ pointers */
static zsock_t *zmq_push;

static netsnmp_callback *
_cb(int operation, netsnmp_session *ss, int reqid,
    netsnmp_pdu *pdu, void *magic)
{
    netsnmp_variable_list *var;
    zmsg_t *_zmqmsg = zmsg_new();
    size_t out_len = 0;
    int buf_over = 0;
    u_char mib_buf[MAX_OID_LEN], *mib_bufp = mib_buf;
    size_t mib_buf_len = -1;
    char str_buf[SPRINT_MAX_LEN], *str_bufp = str_buf;
    size_t str_buf_len = SPRINT_MAX_LEN;

    //_cb = (PyObject *)magic;
    //pid_t proc_id = getpid();
    u_char *_devtype = (u_char *)magic;

    if (_debug_level) {
        printf("### callback op:%d", operation);
        printf(" reqid:%d", reqid);
        printf(" host:%s magic:\"%s\"\n", ss->peername, _devtype);
    }

    zmsg_addstrf(_zmqmsg, "%d", operation);
    zmsg_addstrf(_zmqmsg, "%s", ss->peername);
    zmsg_addstrf(_zmqmsg, "%s", _devtype);
    if (operation == NETSNMP_CALLBACK_OP_RECEIVED_MESSAGE) {
        //var_list = PyList_New(0);
        for (var = pdu->variables; var; var = var->next_variable, out_len = 0) {

            // Get response OID
            netsnmp_sprint_realloc_objid(&mib_bufp, &mib_buf_len,
                                         &out_len, 1, &buf_over,
                                         var->name, var->name_length);
            // Get response text
            snprint_value(str_bufp, str_buf_len, var->name, var->name_length, var);

            // Append Python tuple (type, oid, response) to list
            //PyList_Append(var_list, Py_BuildValue("(iss)", vars->type, mib_bufp, str_bufp));
            zmsg_addstrf(_zmqmsg, "%s|%s|%s", mib_bufp, __get_type_str(var), str_bufp);
            //zmsg_addstrf(_zmqmsg, "%s|%s", mib_bufp, str_bufp);
        }
    }
    //PyObject_CallFunction(_cb, "iiisO", proc_id, operation, reqid, ss->peername, var_list ? var_list : Py_BuildValue("i", 0));
    //zstr_sendf(zmq_push, "{\"pid\":%d,\"op\":%d,\"host\":\"%s\"}", proc_id, operation, ss->peername);
    zmsg_send(&_zmqmsg, zmq_push);
    active_hosts--;
    return (void *)SUCCESS;
}

PyObject *
get_async(PyObject *self, PyObject *args) 
{
  PyObject *hosttuple;
  PyObject *host_iter;
  PyObject *host;
  int timeout;
  int retries;
  int ZMQ_HWM;
  int zmq_linger = -1;
  char *ZMQ_IN;
  int rc;
  //PyObject *py_callback;
  int fds = 0, block = 1;
  netsnmp_large_fd_set lfdset;
  pid_t proc_id = getpid();
  char *snmp_open_err;
  char *snmp_send_err;

    if (!PyArg_ParseTuple(args, "Oiiis", &hosttuple, &timeout, &retries, &ZMQ_HWM, &ZMQ_IN)) {
        PyErr_Format(SNMPError, "get: unable to parse args tuple\n");
        return NULL;
    }
    _debug_level = 0;

    zmq_push = zsock_new(ZMQ_PUSH);
    zsock_set_linger(zmq_push, zmq_linger);
    #if CZMQ_VERSION_MAJOR >= 3
    // >=libzmq3
    zsock_set_sndhwm(zmq_push, ZMQ_HWM);
    zsock_set_rcvhwm(zmq_push, ZMQ_HWM);
    #else
    // libzmq2
    zsock_set_hwm(zmq_push, ZMQ_HWM);
    #endif

    rc = zsock_connect(zmq_push, "%s", ZMQ_IN); assert (rc == 0);
    if (_debug_level) printf("### %s (%d) [ZMQ_%s]\n", ZMQ_IN, rc, zsock_type_str(zmq_push));

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

    if (_debug_level) printf("### %d starting session\n", proc_id);

    host_iter = PyObject_GetIter(hosttuple);

    while (host_iter && (host = PyIter_Next(host_iter))) {
      
      netsnmp_pdu *req;
      netsnmp_session sess, *ss;

      if(!(PyTuple_Check(host))) {
        PyErr_Format(SNMPError, "get: unable to parse host tuple\n");
        return NULL;
      }
      char *name = Py_String(PyTuple_GetItem(host, 0));
      char *comm = Py_String(PyTuple_GetItem(host, 1));
      // devtype string is passed as callback magic below
      // helps us quickly correlate devtype class instance back in Python via callback ZeroMQ message
      char *devtype = Py_String(PyTuple_GetItem(host, 2));
      PyObject *devtype_class = PyTuple_GetItem(host, 3);
      // Get PDU void pointer from the SNMPDevice class/subclass object
      netsnmp_pdu *devtype_pdu = PyLong_AsVoidPtr(PyObject_GetAttrString(devtype_class, "pdu"));

      rc = asprintf(&snmp_open_err, "[%d] snmp_open %s", proc_id, name);
      rc = asprintf(&snmp_send_err, "[%d] snmp_send %s", proc_id, name);

      snmp_sess_init(&sess);

      req = snmp_clone_pdu(devtype_pdu); /* copy PDU */

      sess.version       = SNMP_VERSION_2c;
      sess.peername      = name;
      // milliseconds to microseconds
      sess.timeout       = timeout*1000;
      sess.retries       = retries;
      sess.community     = (u_char *)comm;
      sess.community_len = strlen(comm);
      sess.callback      = (netsnmp_callback)_cb;
      sess.callback_magic= (void *)devtype;

      if (!(ss = snmp_open(&sess))) {
        snmp_perror(snmp_open_err);
        continue;
      }
      if (snmp_send(ss, req)) {
        if (_debug_level) printf("### %d sent request to %s\n", proc_id, ss->peername);
        active_hosts++;
      } else {
        snmp_perror(snmp_send_err);
        snmp_free_pdu(req);
      }
      Py_DECREF(host);
    }
    Py_DECREF(host_iter);
    
    if (_debug_level) printf("### %d starting fd poll\n", proc_id);
    netsnmp_large_fd_set_init(&lfdset, fds);
    while (active_hosts) {
      fds = 0, block = 1;
      struct timeval timeout;
  
      snmp_select_info2(&fds, &lfdset, &timeout, &block);
      if (_debug_level) printf("### %d polling %d FDs\n", proc_id, fds);
      //fds = select(fds, (&lfdset)->lfs_setptr, NULL, NULL, block ? NULL : &timeout);
      fds = netsnmp_large_fd_set_select(fds, &lfdset, NULL, NULL, block ? NULL : &timeout);
  
      if (fds < 0) {
          PyErr_Format(SNMPError, "get: select failed\n");
          return NULL;
      }

      if (_debug_level) printf("### %d polled %d FDs\n", proc_id, fds);
  
      if (fds) {
          snmp_read2(&lfdset);
      } else {
          snmp_timeout();
      }
    }
    // Close SNMP sockets
    snmp_close_sessions();
    // Close ZeroMQ context
    zsock_destroy(&zmq_push);
    return Py_BuildValue("i", SUCCESS);
}
