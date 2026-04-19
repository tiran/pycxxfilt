// SPDX-License-Identifier: Apache-2.0
//
// Shim header for standalone build of LLVM's cxa_demangle.
// Replaces libcxxabi/src/abort_message.h
//
// The original abort_message.h provides __abort_message() which is used by
// DemangleConfig.h via _LIBCPP_VERBOSE_ABORT and by cxa_demangle.cpp via
// _LIBCXXABI_ASSERT. This shim provides compatible definitions using
// standard library functions.

#ifndef PYCXXFILT_ABORT_MESSAGE_H
#define PYCXXFILT_ABORT_MESSAGE_H

#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cassert>

#ifdef __GNUC__
__attribute__((format(printf, 1, 2)))
#endif
static inline void __abort_message(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
    std::abort();
}

// _LIBCXXABI_ASSERT is used in cxa_demangle.cpp to define DEMANGLE_ASSERT
// before DemangleConfig.h is included.
#ifndef _LIBCXXABI_ASSERT
#define _LIBCXXABI_ASSERT(expr, msg) assert((expr) && (msg))
#endif

#endif // PYCXXFILT_ABORT_MESSAGE_H
