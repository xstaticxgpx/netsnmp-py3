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
      *val = (char *)PyUnicode_AsUTF8AndSize(attr, len);
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
__get_type_str (int type)
{
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
            str = "STRING";
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
