# SPDX-License-Identifier: Apache-2.0
"""Tests for pycxxfilt.msvc_demangle().

Bulk cases come from LLVM's ms-*.test files (vendor/test/), parsed with
FileCheck semantics: each ``; CHECK:`` text must appear as a
whitespace-canonicalized substring of the demangler's output.
"""

from __future__ import annotations

import pytest
from conftest import canonicalize_ws, iter_msvc_test_cases

import pycxxfilt

# Inputs where our standalone build differs from LLVM's llvm-undname output.
# The two string-literal cases decode raw bytes differently; the MD5 case
# relies on a CHECK-NEXT continuation line our parser does not reconstruct.
_XFAIL_MANGLED: frozenset[str] = frozenset(
    {
        "??@a6a285da2eea70dba6b578022be61d81@asdf",
        "??_C@_01LOCGONAA@?$AA?$AA@",
        "??_C@_13FFFLPHEM@?$AA?$HO?$AA?$AA@",
    }
)


def test_llvm_msvc_cases() -> None:
    """Run every vendored MSVC demangle vector in one test."""
    failures: list[str] = []
    xfails: list[str] = []
    total = 0
    for mangled, expected, source in iter_msvc_test_cases():
        total += 1
        result = pycxxfilt.msvc_demangle(mangled)
        ok = result is not None and canonicalize_ws(expected) in canonicalize_ws(result)
        if ok:
            continue
        if mangled in _XFAIL_MANGLED:
            xfails.append(mangled)
        else:
            failures.append(
                f"  [{source}] {mangled}\n"
                f"    expected substring: {expected!r}\n"
                f"    got:                {result!r}"
            )
    assert total > 800, f"MSVC corpus not loaded (got {total} cases)"
    if xfails:
        print(f"xfail: {len(xfails)} known output differences")
    if failures:
        header = f"{len(failures)} of {total} MSVC demangle tests failed:\n"
        pytest.fail(header + "\n".join(failures))


class TestMSVCAPI:
    """Test the Python-level API contract."""

    def test_method(self) -> None:
        assert (
            pycxxfilt.msvc_demangle("?foo@Tensor@at@@QEAAXXZ")
            == "public: void __cdecl at::Tensor::foo(void)"
        )

    def test_variable(self) -> None:
        assert pycxxfilt.msvc_demangle("?x@@3HA") == "int x"

    def test_invalid_returns_none(self) -> None:
        assert pycxxfilt.msvc_demangle("not_mangled") is None

    def test_itanium_name_returns_none(self) -> None:
        # No ``?`` prefix -> None, not ValueError.
        assert pycxxfilt.msvc_demangle("_Z3fooi") is None

    def test_empty_string_returns_none(self) -> None:
        assert pycxxfilt.msvc_demangle("") is None

    def test_invalid_msvc_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="invalid MSVC mangled name"):
            pycxxfilt.msvc_demangle("?bad")

    def test_type_error_on_non_string(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.msvc_demangle(42)  # type: ignore[arg-type]

    def test_type_error_on_bytes(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.msvc_demangle(b"?x@@3HA")  # type: ignore[arg-type]
