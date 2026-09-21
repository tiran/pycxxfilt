# SPDX-License-Identifier: Apache-2.0

LLVM_VERSION: str
"""Version of the vendored LLVM demanglers (e.g. ``"23.1.0"``)."""

def itanium_demangle(mangled_name: str, /) -> str | None:
    """Demangle an Itanium C++ ABI name (GCC/Clang, ``_Z...``).

    Returns the demangled name, or None if the input is not a valid mangled
    name.  Raises TypeError for non-str input, and ValueError if the name
    starts with ``_Z`` but is not valid.
    """
    ...

def msvc_demangle(mangled_name: str, /) -> str | None:
    """Demangle an MSVC (Microsoft) name (``?...``).

    Returns the demangled name, or None if the input is not a valid mangled
    name.  Raises TypeError for non-str input, and ValueError if the name
    starts with ``?`` but is not valid.
    """
    ...

def rust_demangle(mangled_name: str, /) -> str | None:
    """Demangle a Rust v0 name (``_R...``).

    Returns the demangled name, or None if the input is not a valid mangled
    name.  Raises TypeError for non-str input, and ValueError if the name
    starts with ``_R`` but is not valid.
    """
    ...
