#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#define SUCCESS 1
#define FAILURE 0

#if PY_MAJOR_VERSION >= 3
#define Py_String PyUnicode_AsUTF8
#else
#define Py_String PyString_AsString
#endif

static int _debug_level;

/* Exceptions */
static PyObject *SNMPError;

/* Functions */
long long __py_attr_long (PyObject *obj, char *attr_name);
void *__py_attr_void_ptr (PyObject *obj, char *attr_name);
int __py_attr_get_string (PyObject *obj, char *attr_name, char **val, Py_ssize_t *len);
int __py_attr_set_string (PyObject *obj, char *attr_name, char *val, size_t len);

char *__get_type_str     (netsnmp_variable_list *var);

/* Synchronous(thread-safe) implementations */
PyObject *create_session (PyObject *self, PyObject *args);
PyObject *get            (PyObject *self, PyObject *args);
// GETNEXT and WALK functionality wrapped ontop of get in Python
PyObject *close_session  (PyObject *self, PyObject *args);

/* Asynchronous implementations */
// Now defined as static in respective source file:
//netsnmp_callback 
//         *get_async_cb   (int operation, netsnmp_session *ss, int reqid, netsnmp_pdu *pdu, void *magic);
PyObject *get_async      (PyObject *self, PyObject *args);

/* Helper functions */
PyObject *build_pdu      (PyObject *self, PyObject *args);
