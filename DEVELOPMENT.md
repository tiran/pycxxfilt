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

The Itanium demangler is vendored from LLVM's libcxxabi, release tag
**llvmorg-22.1.3**. The following files are copied from the LLVM source
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

The update script patches `cxa_demangle.cpp` and `DemangleConfig.h` to
wrap all symbols in a `pycxxfilt` namespace.

Two **shim headers** provide the libcxxabi-internal symbols that the
original code depends on:

- `vendor/abort_message.h` -- replaces `libcxxabi/src/abort_message.h`
- `vendor/__cxxabi_config.h` -- replaces `libcxxabi/include/__cxxabi_config.h`

These shim files must be maintained manually if the upstream API changes.

### Updating to a newer LLVM release

```
./update-vendor.sh llvmorg-XX.Y.Z
```

This downloads all files, applies namespace patches, and records the
tag.  The shim headers are **not** overwritten.  After updating, verify
that the shims are still compatible and run the test suite.

## Releasing

1. Update the version in `pyproject.toml` and `meson.build`.
2. Commit and tag: `git tag v0.1.0`
3. Push the tag: `git push origin v0.1.0`
4. The `build.yml` GitHub Actions workflow builds wheels and sdist, then
   publishes to PyPI via trusted publishing.

PyPI trusted publishing must be configured once:

- Go to PyPI project settings → Publishing → Add a new publisher
- Repository: `tiran/pycxxfilt`
- Workflow: `build.yml`
- Environment: `pypi`
