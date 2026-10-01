# pycxxfilt

[![Version](https://img.shields.io/pypi/v/pycxxfilt.svg?maxAge=86400)](https://pypi.org/project/pycxxfilt/)
[![Supported Versions](https://img.shields.io/pypi/pyversions/pycxxfilt.svg)](https://pypi.org/project/pycxxfilt/)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/tiran/pycxxfilt/badge)](https://scorecard.dev/viewer/?uri=github.com/tiran/pycxxfilt)

Demangle C++ and Rust symbols using LLVM's demanglers.

`pycxxfilt` is a Python C extension that wraps LLVM's standalone demangle
engines. It handles three name-mangling schemes:

- the [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#mangling)
  (`_Z...`), used by GCC (3.0+), Clang, and other compilers on most platforms
- **MSVC** (Microsoft, `?...`), the scheme used by the Visual C++ toolchain
- **Rust** v0 (`_R...`)

The demangler sources are shipped directly, so no external C++ libraries are
required at build time or runtime.

The bundled demangler is from LLVM release `23.1.0`.

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

pycxxfilt.demangle("_Z3fooi")                    # 'foo(int)'
pycxxfilt.demangle("?foo@Tensor@at@@QEAAXXZ")    # 'public: void __cdecl at::Tensor::foo(void)'
pycxxfilt.demangle("_RNvC6_123foo3bar")          # '123foo::bar'
pycxxfilt.demangle("not_mangled")                # None
```

`demangle()` auto-detects the flavor by prefix (`?` -> MSVC, `_R` -> Rust,
otherwise Itanium) and returns the demangled name, or `None` if the input is
not a valid mangled symbol. To force a specific engine, call
`itanium_demangle()`, `msvc_demangle()`, or `rust_demangle()` directly.

Since 1.2.0, `demangle()` accepts an Itanium symbol carrying a trailing GNU
symbol version (`name@VERSION` or the default `name@@VERSION`, as emitted by
`nm`/`readelf`); the version is split off and re-appended to the result:

```python
pycxxfilt.demangle("_Z3fooi@@GLIBCXX_3.4")       # 'foo(int)@@GLIBCXX_3.4'
```

This only applies to the auto-detecting `demangle()`. The flavor-specific
`itanium_demangle()` stays strict and rejects a `@` suffix, and the suffix is
never stripped on the MSVC path, where `@` is a structural separator.

All functions raise `TypeError` for non-string input and `ValueError` when the
input carries a flavor's prefix but fails to demangle. Because the demanglers
are NUL-terminated C APIs, a string containing an embedded NUL byte (`\0`) is
rejected with `ValueError` rather than being silently truncated.

### Command line

```console
$ python -m pycxxfilt _Z3fooi "?x@@3HA" _RNvC1a4main not_mangled
foo(int)
int x
a::main
not_mangled
```

Symbols that are not valid mangled names are printed as-is.

## Supported formats

Two C++ ABIs are decoded — Itanium (`_Z`, GCC/Clang, `itanium_demangle()`) and
MSVC (`?`, `msvc_demangle()`). Coverage tracks the bundled LLVM version.
✅ supported, ❌ not decoded, n/a means the construct does not exist in that ABI.

| Standard | Itanium | MSVC | Feature |
|---|:---:|:---:|---|
| C++98/03 | ✅ | ✅ | namespaces, templates, operator overloads, ctors/dtors, vtables/RTTI |
| C++11 | ✅ | ✅ | lambdas, rvalue references, ref-qualifiers, variadic templates, user-defined literals |
| C++14 | ✅ | ✅ | `decltype(auto)` / deduced return types, variable and generic-lambda templates |
| C++17 | ✅ | ✅ | `noexcept` in the type system |
| C++20 | ✅ | ✅ | `char8_t`, `operator<=>`, `co_await` |
| C++20 | ✅ | ❌ | concepts / `requires`, modules, coroutines |
| C++23 | ✅ | ❌ | explicit object parameter ("deducing this") |
| C++26 | ✅ | ❌ | pack indexing (`T...[N]`) |
| Extension | ✅ | n/a | C23 `_BitInt(N)`, extended FP (`_Float16`, `__float128`) |
| Extension | ✅ | n/a | Objective-C++ protocol qualifiers, GNU/Clang vector types |
| Extension | ✅ | n/a | ABI tags (`[abi:...]`), GCC symbol suffixes (`.cold`, `.clone`) |
| Extension | n/a | ✅ | all calling conventions (`__cdecl`, `__stdcall`, `__vectorcall`, ...) |
| Extension | n/a | ✅ | RTTI descriptors, vftables/vbtables, thunks |
| Extension | n/a | ✅ | encoded string literals, MD5-hashed names |

Rust (`_R`, `rust_demangle()`) decodes the v0 scheme
([RFC 2603](https://rust-lang.github.io/rfcs/2603-rust-symbol-name-mangling-v0.html)):
crate paths, inherent/trait impls, trait definitions, closures/shims, generic
type/const/lifetime arguments, trait objects, const generics, punycode
identifiers, and backreferences. The legacy Rust mangling (`_ZN...`) is not
decoded as Rust; such names fall through to the Itanium demangler.

## Stability

The public API is `pycxxfilt.demangle()`, the flavor-specific
`itanium_demangle()` / `msvc_demangle()` / `rust_demangle()`, and
`pycxxfilt.LLVM_VERSION`. From 1.0 onward it follows
[semantic versioning](https://semver.org/): no breaking changes to these
without a major version bump.

## Comparison with cxxfilt

The [cxxfilt](https://pypi.org/project/cxxfilt/) package uses `ctypes` to
call `__cxa_demangle` from the system's `libstdc++.so`. This means it
depends on a C++ runtime library being installed and available at runtime,
it is not available on Windows, and it only handles Itanium C++ names.

`pycxxfilt` takes a different approach: it ships vendored copies of LLVM's
demangle engines and compiles them into a C extension module. This makes it
self-contained with no runtime dependency on any system C++ library, it works
on Linux, macOS, and Windows, and it demangles MSVC and Rust names in addition
to Itanium C++.

## License

The project code is licensed under the
[Apache License 2.0](LICENSE).

The vendored LLVM demangler is licensed under the
[Apache License 2.0 with LLVM Exceptions](LICENSE.llvm).
