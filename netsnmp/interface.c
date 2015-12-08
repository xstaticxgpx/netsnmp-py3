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

int
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
