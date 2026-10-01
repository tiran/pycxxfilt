// SPDX-License-Identifier: Apache-2.0
//
// CPython extension module wrapping LLVM's name demanglers.
//
// Thin Python bindings to three demanglers from LLVM's standalone LLVMDemangle
// component (vendor/llvm/lib/Demangle), reached via the extern "C" wrappers in
// _llvm_demangle.cpp:
//   * itanium_demangle   -- IA-64 C++ ABI (GCC/Clang), llvm::itaniumDemangle
//   * msvc_demangle      -- MSVC, llvm::microsoftDemangle
//   * rust_demangle      -- Rust v0, llvm::rustDemangle

// Py_LIMITED_API is set by the meson build system.
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <string.h>

// Provided by _llvm_demangle.cpp (extern "C" wrappers around llvm::).
// All three return a malloc'd string on success, or NULL on failure (invalid
// name or allocation failure -- indistinguishable, so OOM is reported the same
// as an invalid name).
extern char *pycxxfilt_itanium_demangle(const char *mangled_name);
extern char *pycxxfilt_microsoft_demangle(const char *mangled_name);
extern char *pycxxfilt_rust_demangle(const char *mangled_name);

// Encode a str argument to a UTF-8 bytes object (new reference), or return
// NULL with an exception set.  Rejects non-str inputs with TypeError, and an
// embedded NUL with ValueError -- the demanglers are NUL-terminated C APIs, so
// a NUL would silently truncate the name.
static PyObject *
encode_arg(PyObject *arg)
{
    if (!PyUnicode_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "argument must be a string");
        return NULL;
    }
    PyObject *bytes = PyUnicode_AsEncodedString(arg, "utf-8", "strict");
    if (bytes == NULL) {
        return NULL;
    }
    char *data;
    Py_ssize_t size;
    if (PyBytes_AsStringAndSize(bytes, &data, &size) < 0) {
        Py_DECREF(bytes);
        return NULL;
    }
    if (memchr(data, '\0', (size_t)size) != NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "mangled name contains an embedded null byte");
        Py_DECREF(bytes);
        return NULL;
    }
    return bytes;
}

// Shared result builder for all three demanglers.  Frees `demangled`; NULL
// maps to ValueError when `looks_mangled` (input has this flavor's prefix),
// else None.  `flavor` names the engine for the error message; `arg` is the
// original str.
static PyObject *
result_from_ptr(char *demangled, int looks_mangled, const char *flavor,
                PyObject *arg)
{
    if (demangled != NULL) {
        PyObject *result = PyUnicode_FromString(demangled);
        free(demangled);
        return result;
    }
    if (looks_mangled) {
        PyErr_Format(PyExc_ValueError, "invalid %s mangled name: %U", flavor,
                     arg);
        return NULL;
    }
    Py_RETURN_NONE;
}

// clang-format off
PyDoc_STRVAR(itanium_demangle_doc,
"itanium_demangle(mangled_name: str, /) -> str | None\n"
"\n"
"Demangle an Itanium C++ ABI name (GCC/Clang, '_Z...').\n"
"\n"
"Returns the demangled name, or None if the input is not a valid\n"
"mangled name.  Raises TypeError if the argument is not a string, and\n"
"ValueError if the name starts with '_Z' but is not valid.\n");
// clang-format on

static PyObject *
pycxxfilt_itanium(PyObject *module, PyObject *arg)
{
    PyObject *bytes = encode_arg(arg);
    if (bytes == NULL) {
        return NULL;
    }
    const char *mangled = PyBytes_AsString(bytes);
    if (mangled == NULL) {
        Py_DECREF(bytes);
        return NULL;
    }
    int looks_mangled = (mangled[0] == '_' && mangled[1] == 'Z');
    char *demangled = pycxxfilt_itanium_demangle(mangled);
    Py_DECREF(bytes);
    return result_from_ptr(demangled, looks_mangled, "Itanium", arg);
}

// clang-format off
PyDoc_STRVAR(rust_demangle_doc,
"rust_demangle(mangled_name: str, /) -> str | None\n"
"\n"
"Demangle a Rust v0 name ('_R...').\n"
"\n"
"Returns the demangled name, or None if the input is not a valid\n"
"mangled name.  Raises TypeError if the argument is not a string, and\n"
"ValueError if the name starts with '_R' but is not valid.\n");
// clang-format on

static PyObject *
pycxxfilt_rust(PyObject *module, PyObject *arg)
{
    PyObject *bytes = encode_arg(arg);
    if (bytes == NULL) {
        return NULL;
    }
    const char *mangled = PyBytes_AsString(bytes);
    if (mangled == NULL) {
        Py_DECREF(bytes);
        return NULL;
    }
    int looks_mangled = (mangled[0] == '_' && mangled[1] == 'R');
    char *demangled = pycxxfilt_rust_demangle(mangled);
    Py_DECREF(bytes);
    return result_from_ptr(demangled, looks_mangled, "Rust", arg);
}

// clang-format off
PyDoc_STRVAR(msvc_demangle_doc,
"msvc_demangle(mangled_name: str, /) -> str | None\n"
"\n"
"Demangle an MSVC (Microsoft) name ('?...').\n"
"\n"
"Returns the demangled name, or None if the input is not a valid\n"
"mangled name.  Raises TypeError if the argument is not a string, and\n"
"ValueError if the name starts with '?' but is not valid.\n");
// clang-format on

static PyObject *
pycxxfilt_microsoft(PyObject *module, PyObject *arg)
{
    PyObject *bytes = encode_arg(arg);
    if (bytes == NULL) {
        return NULL;
    }
    const char *mangled = PyBytes_AsString(bytes);
    if (mangled == NULL) {
        Py_DECREF(bytes);
        return NULL;
    }
    int looks_mangled = (mangled[0] == '?');
    char *demangled = pycxxfilt_microsoft_demangle(mangled);
    Py_DECREF(bytes);
    return result_from_ptr(demangled, looks_mangled, "MSVC", arg);
}

// clang-format off
static PyMethodDef
module_methods[] = {
    {"itanium_demangle", pycxxfilt_itanium, METH_O, itanium_demangle_doc},
    {"msvc_demangle", pycxxfilt_microsoft, METH_O, msvc_demangle_doc},
    {"rust_demangle", pycxxfilt_rust, METH_O, rust_demangle_doc},
    {NULL, NULL, 0, NULL}
};
// clang-format on

#define MODULE_DOC "C++/Rust name demangling using LLVM's demanglers."

// Populate module attributes shared by every build variant.
static int
module_exec(PyObject *module)
{
    // PYCXXFILT_LLVM_VERSION is a compile-time define from the meson build.
    if (PyModule_AddStringConstant(module, "LLVM_VERSION",
                                   PYCXXFILT_LLVM_VERSION) < 0) {
        return -1;
    }
    return 0;
}

#ifdef Py_TARGET_ABI3T
// PEP 803 abi3t (free-threaded stable ABI, 3.15+): PyObject is opaque, so
// export the module from a PEP 793 PySlot array via the PyModExport hook
// instead of a statically allocated PyModuleDef.
PyABIInfo_VAR(abi_info);

// clang-format off
static PySlot
module_slots[] = {
    PySlot_STATIC_DATA(Py_mod_abi, &abi_info),
    PySlot_STATIC_DATA(Py_mod_name, "_cxxfilt"),
    PySlot_STATIC_DATA(Py_mod_doc, MODULE_DOC),
    PySlot_STATIC_DATA(Py_mod_methods, module_methods),
    PySlot_FUNC(Py_mod_exec, module_exec),
    PySlot_DATA(Py_mod_gil, Py_MOD_GIL_NOT_USED),
    PySlot_END
};
// clang-format on

// The hook only returns the static array, so no PyABIInfo_Check is needed.
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
    {Py_mod_exec, (void *)module_exec},
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
