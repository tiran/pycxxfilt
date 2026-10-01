# SPDX-License-Identifier: Apache-2.0
"""pycxxfilt -- demangle C++ and Rust symbols using LLVM's demanglers.

Wraps LLVM's standalone demangle engines for three name-mangling schemes:

* Itanium C++ ABI (GCC 3.0+, Clang, ``_Z...``) -- ``itanium_demangle``
* MSVC (Microsoft, ``?...``) -- ``msvc_demangle``
* Rust v0 (``_R...``) -- ``rust_demangle``

``demangle`` auto-detects the flavor by prefix.  The bundled LLVM version is
available as ``pycxxfilt.LLVM_VERSION``.

Example::

    >>> import pycxxfilt
    >>> pycxxfilt.demangle("_Z3fooi")
    'foo(int)'
    >>> pycxxfilt.demangle("?foo@Tensor@at@@QEAAXXZ")
    'public: void __cdecl at::Tensor::foo(void)'
    >>> pycxxfilt.demangle("_Z3fooi@@GLIBCXX_3.4")
    'foo(int)@@GLIBCXX_3.4'
    >>> pycxxfilt.demangle("not_mangled") is None
    True
    >>> pycxxfilt.demangle("_Zinvalid")
    Traceback (most recent call last):
        ...
    ValueError: invalid Itanium mangled name: _Zinvalid
"""

from pycxxfilt._cxxfilt import (
    LLVM_VERSION,
    itanium_demangle,
    msvc_demangle,
    rust_demangle,
)

__all__ = [
    "LLVM_VERSION",
    "demangle",
    "itanium_demangle",
    "msvc_demangle",
    "rust_demangle",
]


def demangle(mangled_name: str, /) -> str | None:
    """Demangle a mangled name, auto-detecting Itanium, MSVC, or Rust.

    Dispatches by prefix (``?`` -> MSVC, ``_R`` -> Rust, else Itanium); the
    three prefixes are mutually exclusive.  Returns the demangled name, or None
    if the input is not a valid mangled name.  Raises TypeError for non-str
    input and ValueError when the input carries a flavor's prefix but fails to
    demangle, or contains an embedded NUL byte.

    On the Itanium path a trailing GNU symbol version (``name@VER`` or
    ``name@@VER``) is split off and re-appended verbatim.
    """
    if not isinstance(mangled_name, str):
        raise TypeError("demangle() argument must be a string")
    if mangled_name.startswith("?"):
        return msvc_demangle(mangled_name)
    if mangled_name.startswith("_R"):
        return rust_demangle(mangled_name)
    # Strip a GNU symbol version suffix; "@" never occurs in Itanium names.
    name, sep, version = mangled_name.partition("@")
    demangled = itanium_demangle(name)
    if demangled is None or not sep:
        return demangled
    return f"{demangled}{sep}{version}"
