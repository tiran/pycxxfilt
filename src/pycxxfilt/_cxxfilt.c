// SPDX-License-Identifier: Apache-2.0
//
// CPython extension module wrapping LLVM's __cxa_demangle.
//
// This module provides a thin Python binding to the IA-64 C++ ABI name
// demangler from LLVM's libcxxabi (cxa_demangle.cpp).

// Py_LIMITED_API is set by the meson build system.
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>

// Provided by vendor/cxa_demangle.cpp (extern "C" linkage)
extern char *__cxa_demangle(const char *mangled_name, char *buf, size_t *n,
                            int *status);

// __cxa_demangle status codes
#define DEMANGLE_SUCCESS 0
#define DEMANGLE_MEMORY_ALLOC_FAILURE -1
#define DEMANGLE_INVALID_MANGLED_NAME -2
#define DEMANGLE_INVALID_ARGS -3

// clang-format off
PyDoc_STRVAR(demangle_doc,
"demangle(mangled_name: str, /) -> str | None\n"
"\n"
"Demangle a C++ mangled name (IA-64 C++ ABI).\n"
"\n"
"Returns the demangled name as a string, or None if the input\n"
"is not a valid mangled name.\n"
"\n"
"Raises TypeError if the argument is not a string.\n"
"Raises ValueError if the name starts with '_Z' but is not valid.\n");
// clang-format on

static PyObject *
pycxxfilt_demangle(PyObject *module, PyObject *arg)
{
    // Only accept str, not bytes or other types
    if (!PyUnicode_Check(arg)) {
        PyErr_SetString(PyExc_TypeError,
                        "demangle() argument must be a string");
        return NULL;
    }

    // Encode to UTF-8 to get a C string for __cxa_demangle
    PyObject *bytes = PyUnicode_AsEncodedString(arg, "utf-8", "strict");
    if (bytes == NULL) {
        return NULL;
    }
    const char *mangled = PyBytes_AsString(bytes);
    if (mangled == NULL) {
        Py_DECREF(bytes);
        return NULL;
    }

    // Empty string is never a valid mangled name
    if (mangled[0] == '\0') {
        Py_DECREF(bytes);
        Py_RETURN_NONE;
    }

    // Check for "_Z" prefix before releasing bytes
    int has_mangle_prefix = (mangled[0] == '_' && mangled[1] == 'Z');

    int status = 0;
    char *demangled = __cxa_demangle(mangled, NULL, NULL, &status);
    Py_DECREF(bytes);
    // mangled pointer is invalid after Py_DECREF

    switch (status) {
    case DEMANGLE_SUCCESS:
        if (demangled != NULL) {
            PyObject *result = PyUnicode_FromString(demangled);
            free(demangled);
            return result;
        }
        /* fall through -- should not happen */
    case DEMANGLE_INVALID_MANGLED_NAME:
        // "_Z" prefix indicates intent to be a mangled name
        if (has_mangle_prefix) {
            PyErr_Format(PyExc_ValueError, "invalid mangled name: %U", arg);
            return NULL;
        }
        Py_RETURN_NONE;
    case DEMANGLE_MEMORY_ALLOC_FAILURE:
        return PyErr_NoMemory();
    case DEMANGLE_INVALID_ARGS:
        PyErr_SetString(PyExc_RuntimeError,
                        "internal error: invalid arguments to __cxa_demangle");
        return NULL;
    default:
        PyErr_Format(PyExc_RuntimeError,
                     "internal error: __cxa_demangle returned status %d",
                     status);
        return NULL;
    }
}

// clang-format off
static PyMethodDef
module_methods[] = {
    {"demangle", pycxxfilt_demangle, METH_O, demangle_doc},
    {NULL, NULL, 0, NULL}
};
// clang-format on

#define MODULE_DOC "C++ name demangling using LLVM's IA-64 C++ ABI demangler."

#ifdef Py_TARGET_ABI3T
// PEP 803 abi3t (free-threaded stable ABI, 3.15+): PyObject is opaque, so
// export the module from slots via the PEP 793 PyModExport hook instead of a
// statically allocated PyModuleDef.
// clang-format off
static PyModuleDef_Slot
module_slots[] = {
    {Py_mod_name, (void *)"_cxxfilt"},
    {Py_mod_doc, (void *)MODULE_DOC},
    {Py_mod_methods, (void *)module_methods},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};
// clang-format on

PyMODEXPORT_FUNC
PyModExport__cxxfilt(void)
{
    return module_slots;
}

#else
// --- Traditional path: abi3 (<= 3.14) and full (free-threaded) builds ---
// clang-format off
static PyModuleDef_Slot
module_slots[] = {
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static struct PyModuleDef
moduledef = {
    PyModuleDef_HEAD_INIT,
    "_cxxfilt",                                          /* m_name */
    MODULE_DOC,                                          /* m_doc */
    0,                                                   /* m_size */
    module_methods,                                      /* m_methods */
    module_slots,                                        /* m_slots */
};
// clang-format on

PyMODINIT_FUNC
PyInit__cxxfilt(void)
{
    return PyModuleDef_Init(&moduledef);
}
#endif
