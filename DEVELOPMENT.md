# Development

## Prerequisites

- C++20 compiler (GCC, Clang, or MSVC)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Building from source

```
uv venv .venv && source .venv/bin/activate
uv pip install meson-python meson
uv pip install --no-build-isolation -e ".[test]"
python -m pytest tests/ -q
```

## tox environments

```
tox run                 # all test envs + lint + typecheck
tox run -e lint         # ruff check + format check
tox run -e fix          # ruff auto-fix + format
tox run -e typecheck    # ty type checker
tox run -e py314        # run tests with a specific Python version
```

## Vendored LLVM sources

The Itanium demangler is vendored from LLVM's libcxxabi. The exact release
tag is recorded in `vendor/LLVM_TAG` and exposed at runtime as
`pycxxfilt.LLVM_VERSION`. The following files are copied from the LLVM source
tree:

| Local path | LLVM source |
|---|---|
| `vendor/cxa_demangle.cpp` | `libcxxabi/src/cxa_demangle.cpp` |
| `vendor/demangle/DemangleConfig.h` | `libcxxabi/src/demangle/DemangleConfig.h` |
| `vendor/demangle/ItaniumDemangle.h` | `libcxxabi/src/demangle/ItaniumDemangle.h` |
| `vendor/demangle/ItaniumNodes.def` | `libcxxabi/src/demangle/ItaniumNodes.def` |
| `vendor/demangle/StringViewExtras.h` | `libcxxabi/src/demangle/StringViewExtras.h` |
| `vendor/demangle/Utility.h` | `libcxxabi/src/demangle/Utility.h` |
| `vendor/demangle/README.txt` | `libcxxabi/src/demangle/README.txt` |
| `vendor/DemangleTestCases.inc` | `libcxxabi/test/DemangleTestCases.inc` |
| `LICENSE.llvm` | `llvm/LICENSE.TXT` |

The vendored sources are copied verbatim -- the update script does not patch
them. Symbol isolation instead comes from the demangler's own anonymous
namespace (`DEMANGLE_NAMESPACE_BEGIN` in `vendor/demangle/DemangleConfig.h`)
combined with `gnu_symbol_visibility: 'hidden'` in the meson build, so none of
the demangler symbols are exported from the extension.

Two **shim headers** provide the libcxxabi-internal symbols that the
original code depends on:

- `vendor/abort_message.h` -- replaces `libcxxabi/src/abort_message.h`
- `vendor/__cxxabi_config.h` -- replaces `libcxxabi/include/__cxxabi_config.h`

These shim files must be maintained manually if the upstream API changes.

### Updating to a newer LLVM release

```
./update-vendor.sh llvmorg-XX.Y.Z
```

This downloads all files, records the tag in `vendor/LLVM_TAG`, and updates the
version mentioned in `README.md` to match. The extension exposes that version as
`LLVM_VERSION`; the meson build reads `vendor/LLVM_TAG` and passes the value to
the C extension as a compile-time define (see `src/pycxxfilt/meson.build`), so it
always matches the tag. The shim headers are **not** overwritten.  After
updating, verify that the shims are still compatible and run the test suite.

## Releasing

The package version is derived from the latest git tag by vcs-versioning,
so there is no version string to edit by hand.

1. Tag the release: `git tag v0.1.0`
2. Push the tag: `git push origin v0.1.0`
3. The `build.yml` GitHub Actions workflow builds wheels and sdist, then
   publishes to PyPI via trusted publishing.

PyPI trusted publishing must be configured once:

- Go to PyPI project settings → Publishing → Add a new publisher
- Repository: `tiran/pycxxfilt`
- Workflow: `build.yml`
- Environment: `pypi`
