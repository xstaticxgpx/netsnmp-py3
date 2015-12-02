#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

static char module_docstring[] =
    "Python3 NET-SNMP C Extension";
static char create_session_docstring[] =
    "Create SNMP session";
static char close_session_docstring[] =
    "Close SNMP session";
static char get_docstring[] =
    "Perform SNMPGET request";
static char getnext_docstring[] =
    "Perform SNMPGETNEXT request";
static char walk_docstring[] =
    "Perform SNMPWALK request";

/* Define python interface */

static PyMethodDef APIMethods[] = {
    {"create_session", create_session, METH_VARARGS, create_session_docstring},
    {"get", get, METH_VARARGS, get_docstring},
    {"getnext", getnext, METH_VARARGS, getnext_docstring},
    {"walk", walk, METH_VARARGS, walk_docstring},
    {"close_session", close_session, METH_VARARGS, close_session_docstring},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef API = {
    PyModuleDef_HEAD_INIT,
    "netsnmp._api",      /* m_name */
    "NET-SNMP API",      /* m_doc */
    -1,                  /* m_size */
    APIMethods,          /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
};

PyMODINIT_FUNC
PyInit__api(void)
{
    PyObject *m;

    m = PyModule_Create(&API);
    if (m == NULL)
        return NULL;

    // Define SNMPError exception
    SNMPError = PyErr_NewException("netsnmp._api.SNMPError", NULL, NULL);
    Py_INCREF(SNMPError);
    PyModule_AddObject(m, "SNMPError", SNMPError);

    return m;
}
