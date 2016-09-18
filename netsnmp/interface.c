#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

long long
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

void *
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

int
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
      *val = (char *)Py_String(attr);
      Py_DECREF(attr);
      ret++;
    }
  }
  //printf("%s\n", "test-return");
  return ret;
}

int
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

char *
__get_type_str (netsnmp_variable_list *var)
{
   int hex = 0, x = 0;
   u_char *cp;
   int type = var->type;
   char *str;
   switch (type) {
    case ASN_BOOLEAN:
            str = "BOOLEAN";
            break;
    case ASN_INTEGER:
            str = "INTEGER";
            break;
    case ASN_BIT_STR:
            str = "BITSTR";
            break;
    case ASN_OCTET_STR:
            // Check for any non-printable/non-space character, and mark as hex
            // altered slightly from netsnmp/mib.c:sprint_realloc_octet_string
            for (cp = var->val.string, x = 0; x < (int) var->val_len; x++, cp++) {
                 if (!isprint(*cp) && !isspace(*cp)) {
                     hex = 1;
                     break;
                 }
            }
            str = hex ? "Hex-STRING" : "STRING";
            break;
    case ASN_NULL:
            str = "NULL";
            break;
    case ASN_OBJECT_ID:
            str = "OID";
            break;
    case ASN_SEQUENCE:
            str = "SEQUENCE";
            break;
    case ASN_SET:
            str = "SET";
            break;
    case ASN_TIMETICKS:
            str = "Timeticks";
            break;
    case ASN_COUNTER:
            str = "Counter32";
            break;
    case ASN_OPAQUE:
            str = "Opaque";
            break;
    case ASN_COUNTER64:
            str = "Counter64";
            break;
    case ASN_INTEGER64:
            str = "Integer64";
            break;
    case ASN_GAUGE:
            str = "Gauge32";
            break;
    case ASN_IPADDRESS:
            str = "IpAddress";
            break;
    // Errors:
    case SNMP_ENDOFMIBVIEW:
            str = "ENDOFMIBVIEW";
            break;
    case SNMP_NOSUCHOBJECT:
            str = "NOSUCHOBJECT";
            break;
    case SNMP_NOSUCHINSTANCE:
            str = "NOSUCHINSTANCE";
            break;
    default: /* unconfigured types for now */
            str = "UNKNOWN";
   }
   return str;
}

PyObject *
build_pdu(PyObject *self, PyObject *args)
{
   char *_oidstr;
   size_t oid_arr_len = MAX_OID_LEN;
   oid oid_arr[MAX_OID_LEN], *oid_arr_ptr = oid_arr;
   PyObject *oids;
   PyObject *oids_iter;
   PyObject *var;
   netsnmp_pdu *pdu;
   netsnmp_session nullss;

   if (!PyArg_ParseTuple(args, "O", &oids)) {
       PyErr_Format(SNMPError, "build_pdu: unable to parse args tuple\n");
       return NULL;
   }

   //snmp_set_do_debugging(0);
   // Need to initialize session before OIDs can be parsed
   snmp_disable_stderrlog();
   netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DONT_PERSIST_STATE, 1);
   netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_LOAD, 1);
   netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DISABLE_PERSISTENT_SAVE, 1);
   netsnmp_set_mib_directory("/dev/null");
   set_configuration_directory("/dev/null");
   snmp_sess_init(&nullss);

   pdu = snmp_pdu_create(SNMP_MSG_GET);
   oids_iter = PyObject_GetIter(oids);
   if (oids_iter)
   for ( ; (var = PyIter_Next(oids_iter)); (oid_arr_len = MAX_OID_LEN)) {
       _oidstr = Py_String(var);

       if (!_oidstr) {
           Py_DECREF(oids_iter);
           Py_DECREF(var);
           snmp_free_pdu(pdu);
           PyErr_Format(SNMPError, "build_pdu: wrong Python str conversion\n");
           return NULL;
       }
       if (!snmp_parse_oid(_oidstr, oid_arr_ptr, &oid_arr_len)) {
           Py_DECREF(_oidstr);
           Py_DECREF(oids_iter);
           Py_DECREF(var);
           snmp_free_pdu(pdu);
           PyErr_Format(SNMPError, "build_pdu: unknown object ID (%s)\n", (_oidstr ? _oidstr : "<null>"));
           return NULL;
       }
       snmp_add_null_var(pdu, oid_arr_ptr, oid_arr_len);
       Py_DECREF(var);
   }
   Py_XDECREF(oids_iter);

   return PyLong_FromVoidPtr((void *)pdu);
}
