# SPDX-License-Identifier: Apache-2.0

LLVM_VERSION: str
"""Version of the vendored LLVM demangler (e.g. ``"23.1.0"``)."""

def demangle(mangled_name: str, /) -> str | None:
    """Demangle a C++ mangled name (IA-64 C++ ABI).

    Returns the demangled name as a string, or None if the input
    is not a valid mangled name.

    Raises TypeError if the argument is not a string.
    Raises ValueError if the name starts with '_Z' but is not valid.
    """
    ...
