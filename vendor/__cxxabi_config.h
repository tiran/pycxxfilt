// SPDX-License-Identifier: Apache-2.0
//
// Shim header for standalone build of LLVM's cxa_demangle.
// Replaces libcxxabi/include/__cxxabi_config.h
//
// Only the macros actually used by cxa_demangle.cpp are defined here.

#ifndef PYCXXFILT_CXXABI_CONFIG_H
#define PYCXXFILT_CXXABI_CONFIG_H

// _LIBCXXABI_FUNC_VIS controls symbol visibility for the ABI functions.
// For our standalone build, we don't need special visibility.
#ifndef _LIBCXXABI_FUNC_VIS
#define _LIBCXXABI_FUNC_VIS
#endif

#endif // PYCXXFILT_CXXABI_CONFIG_H
