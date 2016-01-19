#include <Python.h>
#include <_api.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

static char create_session_docstring[] =
    "Create SNMP session";
static char close_session_docstring[] =
    "Close SNMP session";
static char get_docstring[] =
    "Perform SNMPGET request";
static char get_async_docstring[] =
    "Perform asynchronous SNMPGET requests";

/* Define python interface */

static PyMethodDef APIMethods[] = {
    {"create_session", create_session, METH_VARARGS, create_session_docstring},
    {"get", get, METH_VARARGS, get_docstring},
    {"get_async", get_async, METH_VARARGS, get_async_docstring},
    {"close_session", close_session, METH_VARARGS, close_session_docstring},
    {"build_pdu", build_pdu, METH_VARARGS, "Build SNMP PDU object"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3
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
#endif

static PyObject *
api_init(void)
{
    PyObject *m;

#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&API);
#else
    m = Py_InitModule("netsnmp._api", APIMethods);
#endif
    if (m == NULL)
        return NULL;

    // Define SNMPError exception
    SNMPError = PyErr_NewException("netsnmp._api.SNMPError", NULL, NULL);
    Py_INCREF(SNMPError);
    PyModule_AddObject(m, "SNMPError", SNMPError);

    return m;
}


PyMODINIT_FUNC
#if PY_MAJOR_VERSION < 3
init_api(void) {
    api_init();
}
#else
PyInit__api(void) {
    return api_init();
}
#endif
