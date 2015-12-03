#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
//#define MAX_OID_LEN = 128
#define MAX_TYPE_NAME_LEN 32
#define STR_BUF_SIZE (MAX_TYPE_NAME_LEN * MAX_OID_LEN)

#define SUCCESS 1
#define FAILURE 0


int _debug_level;

/* Exceptions */
PyObject *SNMPError;

/* Functions */
long long __py_attr_long (PyObject *obj, char *attr_name);
void *__py_attr_void_ptr (PyObject *obj, char *attr_name);
int __py_attr_get_string (PyObject *obj, char *attr_name, char **val, Py_ssize_t *len);
int __py_attr_set_string (PyObject *obj, char *attr_name, char *val, size_t len);

int __get_type_str       (int type, char *str);

netsnmp_callback 
        *async_callback  (int operation, netsnmp_session *ss, int reqid, netsnmp_pdu *pdu, void *magic);

PyObject *create_session (PyObject *self, PyObject *args);
PyObject *get            (PyObject *self, PyObject *args);
PyObject *getnext        (PyObject *self, PyObject *args);
PyObject *walk           (PyObject *self, PyObject *args);
PyObject *get_async      (PyObject *self, PyObject *args);
PyObject *close_session  (PyObject *self, PyObject *args);
