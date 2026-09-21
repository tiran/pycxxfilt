/* SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception */
/*
 * Minimal shim for llvm/Config/llvm-config.h.
 *
 * This is NOT a copy of LLVM's generated header.  The vendored MSVC/Rust
 * demangler pulls in llvm/Demangle/DemangleConfig.h, which includes this file
 * solely to learn whether LLVM_ENABLE_LLVM_EXPORT_ANNOTATIONS is defined.
 *
 * We intentionally leave that macro undefined so DEMANGLE_ABI expands to
 * nothing; combined with gnu_symbol_visibility: 'hidden' in the meson build,
 * none of the demangler symbols are exported from the extension.
 *
 * Maintain this shim by hand if the upstream expectations change (see
 * DEVELOPMENT.md); update-vendor.sh does not overwrite it.
 */

#ifndef PYCXXFILT_LLVM_CONFIG_SHIM_H
#define PYCXXFILT_LLVM_CONFIG_SHIM_H

/* Intentionally empty: LLVM_ENABLE_LLVM_EXPORT_ANNOTATIONS stays undefined. */

#endif /* PYCXXFILT_LLVM_CONFIG_SHIM_H */
