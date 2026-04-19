# SPDX-License-Identifier: Apache-2.0
"""pycxxfilt -- demangle C++ symbols using LLVM's IA-64 C++ ABI demangler.

Handles the name mangling scheme used by GCC (3.0+), Clang (1.0+), and
other compilers based on the Itanium C++ ABI.  The demangler is
extracted from LLVM's libcxxabi (release tag: llvmorg-22.1.3).

Example::

    >>> import pycxxfilt
    >>> pycxxfilt.demangle("_Z3fooi")
    'foo(int)'
    >>> pycxxfilt.demangle("not_mangled") is None
    True
    >>> pycxxfilt.demangle("_Zinvalid")
    Traceback (most recent call last):
        ...
    ValueError: invalid mangled name: _Zinvalid
"""

from pycxxfilt._cxxfilt import demangle

__all__ = ["demangle"]
