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

All three demanglers (Itanium, MSVC, Rust) are vendored from LLVM's standalone
`LLVMDemangle` component. The exact release tag is recorded in `vendor/LLVM_TAG`
and exposed at runtime as `pycxxfilt.LLVM_VERSION`. The following files are
copied verbatim from the LLVM source tree:

| Local path | LLVM source |
|---|---|
| `vendor/llvm/lib/Demangle/ItaniumDemangle.cpp` | `llvm/lib/Demangle/ItaniumDemangle.cpp` |
| `vendor/llvm/lib/Demangle/MicrosoftDemangle.cpp` | `llvm/lib/Demangle/MicrosoftDemangle.cpp` |
| `vendor/llvm/lib/Demangle/MicrosoftDemangleNodes.cpp` | `llvm/lib/Demangle/MicrosoftDemangleNodes.cpp` |
| `vendor/llvm/lib/Demangle/RustDemangle.cpp` | `llvm/lib/Demangle/RustDemangle.cpp` |
| `vendor/llvm/include/llvm/Demangle/Demangle.h` | `llvm/include/llvm/Demangle/Demangle.h` |
| `vendor/llvm/include/llvm/Demangle/DemangleConfig.h` | `llvm/include/llvm/Demangle/DemangleConfig.h` |
| `vendor/llvm/include/llvm/Demangle/ItaniumDemangle.h` | `llvm/include/llvm/Demangle/ItaniumDemangle.h` |
| `vendor/llvm/include/llvm/Demangle/ItaniumNodes.def` | `llvm/include/llvm/Demangle/ItaniumNodes.def` |
| `vendor/llvm/include/llvm/Demangle/MicrosoftDemangle.h` | `llvm/include/llvm/Demangle/MicrosoftDemangle.h` |
| `vendor/llvm/include/llvm/Demangle/MicrosoftDemangleNodes.h` | `llvm/include/llvm/Demangle/MicrosoftDemangleNodes.h` |
| `vendor/llvm/include/llvm/Demangle/StringViewExtras.h` | `llvm/include/llvm/Demangle/StringViewExtras.h` |
| `vendor/llvm/include/llvm/Demangle/Utility.h` | `llvm/include/llvm/Demangle/Utility.h` |
| `vendor/test/DemangleTestCases.inc` | `libcxxabi/test/DemangleTestCases.inc` |
| `vendor/test/ms-*.test`, `vendor/test/rust.test` | `llvm/test/Demangle/*.test` |
| `LICENSE.llvm` | `llvm/LICENSE.TXT` |

The vendored sources are copied verbatim -- the update script does not patch
them. Symbol isolation comes from leaving `DEMANGLE_ABI` empty (see the shim
below) combined with `gnu_symbol_visibility: 'hidden'` in the meson build, so
none of the demangler symbols are exported from the extension.

One **shim header** is maintained by hand (not downloaded by the update script):

- `vendor/llvm/include/llvm/Config/llvm-config.h` -- LLVM's `DemangleConfig.h`
  includes it only to learn whether `LLVM_ENABLE_LLVM_EXPORT_ANNOTATIONS` is
  defined; leaving it undefined makes `DEMANGLE_ABI` expand to nothing.

This shim must be maintained manually if the upstream expectations change.

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
