#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Update vendored LLVM demangle files from a release tag.
#
# Usage:
#   ./update-vendor.sh                  # uses default tag
#   ./update-vendor.sh llvmorg-23.1.0   # uses specified tag
#
# The demanglers (Itanium, MSVC, Rust) all come from the standalone LLVMDemangle
# component:
#   https://github.com/llvm/llvm-project/tree/<tag>/llvm/lib/Demangle/
#   https://github.com/llvm/llvm-project/tree/<tag>/llvm/include/llvm/Demangle/
# The test corpus comes from libcxxabi.
#
# The hand-written shim header (vendor/llvm/include/llvm/Config/llvm-config.h) is
# NOT overwritten.
set -euo pipefail

DEFAULT_TAG="llvmorg-23.1.0"
TAG="${1:-$DEFAULT_TAG}"
BASE="https://raw.githubusercontent.com/llvm/llvm-project/${TAG}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/vendor"
LLVM_DIR="${VENDOR_DIR}/llvm"

echo "Updating vendored files from ${TAG} ..."

mkdir -p "${LLVM_DIR}/include/llvm/Demangle" "${LLVM_DIR}/lib/Demangle"

# Demangler implementations (llvm/lib/Demangle). ItaniumDemangle.cpp also
# provides itaniumDemangle() and OutputBuffer's vtable, which the MSVC and Rust
# demanglers link against.
for file in ItaniumDemangle.cpp MicrosoftDemangle.cpp \
            MicrosoftDemangleNodes.cpp RustDemangle.cpp; do
    curl -fsSL -o "${LLVM_DIR}/lib/Demangle/${file}" \
        "${BASE}/llvm/lib/Demangle/${file}"
done

# Public and internal headers (llvm/include/llvm/Demangle).
for file in Demangle.h DemangleConfig.h \
            ItaniumDemangle.h ItaniumNodes.def \
            MicrosoftDemangle.h MicrosoftDemangleNodes.h \
            StringViewExtras.h Utility.h; do
    curl -fsSL -o "${LLVM_DIR}/include/llvm/Demangle/${file}" \
        "${BASE}/llvm/include/llvm/Demangle/${file}"
done

# Test corpora live together under vendor/test/ (see tests/conftest.py).
TEST_DIR="${VENDOR_DIR}/test"
mkdir -p "${TEST_DIR}"

# Itanium test corpus (~30 000 mangled/demangled pairs) from libcxxabi.
curl -fsSL -o "${TEST_DIR}/DemangleTestCases.inc" \
    "${BASE}/libcxxabi/test/DemangleTestCases.inc"

# MSVC and Rust test corpora: LLVM's FileCheck-based lit tests.
# ms-options.test and invalid-manglings.test are intentionally excluded --
# they exercise non-default flags / error output.
for file in ms-arg-qualifiers ms-auto-templates ms-back-references ms-basic \
            ms-conversion-operators ms-cxx11 ms-cxx14 ms-cxx17-noexcept \
            ms-cxx20 ms-mangle ms-md5 ms-nested-scopes ms-operators \
            ms-placeholder-return-type ms-ptrauth ms-return-qualifiers \
            ms-string-literals ms-template-callback ms-templates-memptrs-2 \
            ms-templates-memptrs ms-templates ms-thunks ms-windows rust; do
    curl -fsSL -o "${TEST_DIR}/${file}.test" \
        "${BASE}/llvm/test/Demangle/${file}.test"
done

curl -fsSL -o "${SCRIPT_DIR}/LICENSE.llvm" \
    "${BASE}/llvm/LICENSE.TXT"

# Record which tag was used
echo "${TAG}" > "${VENDOR_DIR}/LLVM_TAG"

# Update the README version to match. The extension gets LLVM_VERSION from
# vendor/LLVM_TAG at build time, so nothing to update there.
LLVM_VERSION="${TAG#llvmorg-}"

sed -i -E "s/(LLVM release \`)[^\`]*(\`)/\1${LLVM_VERSION}\2/" \
    "${SCRIPT_DIR}/README.md"

echo "Done.  Vendored files updated to ${TAG} (version ${LLVM_VERSION})."
echo "Note: the shim vendor/llvm/include/llvm/Config/llvm-config.h is kept as-is."
