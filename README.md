# pycxxfilt

[![Version](https://img.shields.io/pypi/v/pycxxfilt.svg?maxAge=86400)](https://pypi.org/project/pycxxfilt/)
[![Supported Versions](https://img.shields.io/pypi/pyversions/pycxxfilt.svg)](https://pypi.org/project/pycxxfilt/)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/tiran/pycxxfilt/badge)](https://scorecard.dev/viewer/?uri=github.com/tiran/pycxxfilt)

Demangle C++ symbols using LLVM's IA-64 C++ ABI demangler.

`pycxxfilt` is a Python C extension that wraps the C++ name demangler
from LLVM's libcxxabi. It handles the name mangling scheme defined by
the [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#mangling),
which is the standard used by GCC (3.0+), Clang (1.0+), and other
compilers on most platforms. The demangler source is shipped directly,
so no external C++ libraries are required at build time or runtime.

## Installation

```console
pip install pycxxfilt
```

Wheels are available for Linux (x86_64, aarch64, ppc64le, s390x), macOS
(x86_64, arm64), and Windows (AMD64). The extension uses the Python
stable ABI (abi3), so a single wheel works with Python 3.11 and later.

## Usage

### Python API

```python
import pycxxfilt

pycxxfilt.demangle("_Z3fooi")          # 'foo(int)'
pycxxfilt.demangle("_ZN3Foo3barEv")    # 'Foo::bar()'
pycxxfilt.demangle("_ZSt4cout")        # 'std::cout'
pycxxfilt.demangle("not_mangled")      # None
```

`demangle()` returns the demangled name as a string, or `None` if the
input is not a valid mangled symbol.

### Command line

```console
$ python -m pycxxfilt _Z3fooi _ZN3Foo3barEv _ZSt4cout not_mangled
foo(int)
Foo::bar()
std::cout
not_mangled
```

Symbols that are not valid mangled names are printed as-is.

## Comparison with cxxfilt

The [cxxfilt](https://pypi.org/project/cxxfilt/) package uses `ctypes` to
call `__cxa_demangle` from the system's `libstdc++.so`. This means it
depends on a C++ runtime library being installed and available at runtime,
and it is not available on Windows.

`pycxxfilt` takes a different approach: it ships a vendored copy of LLVM's
`__cxa_demangle` implementation and compiles it into a C extension module.
This makes it self-contained with no runtime dependency on any system C++
library, and it works on Linux, macOS, and Windows.

## License

The project code is licensed under the
[Apache License 2.0](LICENSE).

The vendored LLVM demangler is licensed under the
[Apache License 2.0 with LLVM Exceptions](LICENSE.llvm).
