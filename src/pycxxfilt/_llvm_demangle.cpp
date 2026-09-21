// SPDX-License-Identifier: Apache-2.0
//
// C-linkage wrappers around LLVM's demanglers.
//
// itaniumDemangle(), microsoftDemangle() and rustDemangle() all live in the
// standalone LLVMDemangle component (llvm/lib/Demangle) and take
// std::string_view, so the C extension (_cxxfilt.c) cannot call them directly.
// These thin extern "C" shims give it a stable C interface.

#include "llvm/Demangle/Demangle.h"

extern "C" {

// Demangle an Itanium C++ ABI (GCC/Clang, `_Z...`) mangled name.  Returns a
// malloc'd, NUL-terminated string on success (caller frees), or NULL on
// failure (invalid name or allocation failure -- indistinguishable here).
char *
pycxxfilt_itanium_demangle(const char *mangled_name)
{
    return llvm::itaniumDemangle(mangled_name);
}

// Demangle an MSVC (Microsoft, `?...`) mangled name.  Returns a malloc'd,
// NUL-terminated string on success (caller frees), or NULL on failure.  We
// discard microsoftDemangle's status out-param: NULL is the only failure
// signal we need, matching the itanium/rust wrappers.
char *
pycxxfilt_microsoft_demangle(const char *mangled_name)
{
    return llvm::microsoftDemangle(mangled_name, /*n_read=*/nullptr,
                                   /*status=*/nullptr);
}

// Demangle a Rust v0 (`_R...`) mangled name.  Returns a malloc'd,
// NUL-terminated string on success (caller frees), or NULL on failure.  There
// is no status out-parameter; NULL is the only failure signal.
char *
pycxxfilt_rust_demangle(const char *mangled_name)
{
    return llvm::rustDemangle(mangled_name);
}

} // extern "C"
