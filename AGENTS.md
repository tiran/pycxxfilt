# SPDX-License-Identifier: Apache-2.0

# Agent instructions

## Project structure

`pycxxfilt` is a thin CPython extension wrapping LLVM's standalone demangle
engines (Itanium, MSVC, Rust).

```
src/pycxxfilt/
  _cxxfilt.c          C extension: itanium/microsoft/rust_demangle (limited API)
  _llvm_demangle.cpp  extern "C" wrappers around the C++ llvm:: demanglers
  __init__.py         public API + demangle() prefix auto-dispatcher
  __main__.py         `python -m pycxxfilt` CLI
  meson.build         builds the llvm_demangle static lib + the extension
vendor/llvm/          LLVM sources, verbatim (see DEVELOPMENT.md)
  include/llvm/Demangle/   demangler headers
  include/llvm/Config/     llvm-config.h shim (hand-written, not vendored)
  lib/Demangle/            demangler .cpp sources
vendor/test/          test corpora: DemangleTestCases.inc, ms-*.test, rust.test
tests/                pytest suite (conftest.py parses the vendored corpora)
update-vendor.sh      refreshes vendor/ from an llvmorg-* tag
```

The three demanglers share one static library; `ItaniumDemangle.cpp` also
supplies `OutputBuffer`'s vtable, which the MSVC/Rust engines link against.

## Setup

Use [uv](https://docs.astral.sh/uv/) to create a venv and install
dependencies:

```
uv venv .venv && source .venv/bin/activate
uv pip install meson-python meson
uv pip install --no-build-isolation -e ".[test]"
```

## Testing

Run the test suite with pytest:

```
python -m pytest tests/ -q
```

## tox

Use tox for the full CI matrix (lint, typecheck, tests across Python
versions):

```
tox run                 # all environments
tox run -e lint         # ruff check + format check
tox run -e fix          # ruff auto-fix + format
tox run -e typecheck    # ty type checker
tox run -e py314        # tests with specific Python version
```

## Commits

Always sign off commits with a `Signed-off-by` trailer (DCO):

```
git commit -s
```
