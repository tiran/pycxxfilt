# SPDX-License-Identifier: Apache-2.0
"""Tests for pycxxfilt.rust_demangle().

Bulk cases come from LLVM's rust.test (vendor/test/rust.test), parsed with
FileCheck's --match-full-lines semantics.  Invalid manglings that llvm-cxxfilt
passes through unchanged (expected == mangled) are ones our API rejects with
ValueError, since they carry the ``_R`` prefix.
"""

from __future__ import annotations

import pytest
from conftest import canonicalize_ws, iter_rust_test_cases

import pycxxfilt


def test_llvm_rust_cases() -> None:
    """Run every vendored Rust demangle vector in one test."""
    failures: list[str] = []
    total = 0
    for mangled, expected in iter_rust_test_cases():
        total += 1
        if expected == mangled:
            # Invalid mangling: llvm-cxxfilt passes it through; we raise.
            try:
                pycxxfilt.rust_demangle(mangled)
            except ValueError:
                continue
            failures.append(f"  {mangled}\n    expected: ValueError")
            continue
        result = pycxxfilt.rust_demangle(mangled)
        if result is None or canonicalize_ws(result) != canonicalize_ws(expected):
            failures.append(
                f"  {mangled}\n    expected: {expected!r}\n    got:      {result!r}"
            )
    assert total > 100, f"Rust corpus not loaded (got {total} cases)"
    if failures:
        header = f"{len(failures)} of {total} Rust demangle tests failed:\n"
        pytest.fail(header + "\n".join(failures))


class TestRustAPI:
    """Test the Python-level API contract."""

    def test_simple(self) -> None:
        assert pycxxfilt.rust_demangle("_RNvC6_123foo3bar") == "123foo::bar"

    def test_crate_path(self) -> None:
        assert pycxxfilt.rust_demangle("_RNvC1a4main") == "a::main"

    def test_invalid_returns_none(self) -> None:
        assert pycxxfilt.rust_demangle("not_mangled") is None

    def test_itanium_name_returns_none(self) -> None:
        # A valid Itanium name is not Rust; no _R prefix -> None, not ValueError.
        assert pycxxfilt.rust_demangle("_Z3fooi") is None

    def test_empty_string_returns_none(self) -> None:
        assert pycxxfilt.rust_demangle("") is None

    def test_invalid_rust_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="invalid Rust mangled name"):
            pycxxfilt.rust_demangle("_Rbad")

    def test_type_error_on_non_string(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.rust_demangle(42)  # type: ignore[arg-type]

    def test_type_error_on_bytes(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.rust_demangle(b"_RNvC1a4main")  # type: ignore[arg-type]
