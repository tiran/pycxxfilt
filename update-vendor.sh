#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Update vendored LLVM demangle files from a release tag.
#
# Usage:
#   ./update-vendor.sh                  # uses default tag
#   ./update-vendor.sh llvmorg-22.1.4   # uses specified tag
#
# Files are downloaded from:
#   https://github.com/llvm/llvm-project/tree/<tag>/libcxxabi/src/
#
# The shim headers (abort_message.h, __cxxabi_config.h) are NOT overwritten.
set -euo pipefail

DEFAULT_TAG="llvmorg-23.1.0"
TAG="${1:-$DEFAULT_TAG}"
BASE="https://raw.githubusercontent.com/llvm/llvm-project/${TAG}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/vendor"

echo "Updating vendored files from ${TAG} ..."

mkdir -p "${VENDOR_DIR}/demangle"

curl -fsSL -o "${VENDOR_DIR}/cxa_demangle.cpp" \
    "${BASE}/libcxxabi/src/cxa_demangle.cpp"

for file in DemangleConfig.h ItaniumDemangle.h ItaniumNodes.def \
            StringViewExtras.h Utility.h README.txt; do
    curl -fsSL -o "${VENDOR_DIR}/demangle/${file}" \
        "${BASE}/libcxxabi/src/demangle/${file}"
done

curl -fsSL -o "${VENDOR_DIR}/DemangleTestCases.inc" \
    "${BASE}/libcxxabi/test/DemangleTestCases.inc"

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
