# SPDX-License-Identifier: Apache-2.0
"""Tests for pycxxfilt.demangle().

The bulk of the test cases come from LLVM's DemangleTestCases.inc
(libcxxabi/test/DemangleTestCases.inc, tag llvmorg-22.1.3) which
contains ~30 000 mangled/demangled pairs.
"""

from __future__ import annotations

import pytest
from conftest import iter_demangle_test_cases

import pycxxfilt

# Cases where our standalone build produces different output than the
# expected string in DemangleTestCases.inc.  This can happen due to
# compiler/optimiser differences.  Tracked here so the rest of the
# ~30 000 cases still run as hard failures.
_XFAIL_MANGLED: frozenset[str] = frozenset(
    {
        # GCC miscompiles ref-qualifier printing for these symbols.
        "_Z1fM1XVKFivEMS_VFivEMS_KOFivE",
        "_Z1fM1XRFivEMS_OFivEMS_KOFivE",
    }
)


# ---------------------------------------------------------------------------
# LLVM bulk tests
# ---------------------------------------------------------------------------


def test_llvm_demangle_cases() -> None:
    """Run all ~30 000 LLVM demangle test vectors in a single test."""
    failures: list[str] = []
    xfails: list[str] = []
    total = 0
    for mangled, expected in iter_demangle_test_cases():
        total += 1
        result = pycxxfilt.demangle(mangled)
        if result != expected:
            if mangled in _XFAIL_MANGLED:
                xfails.append(mangled)
            else:
                failures.append(
                    f"  {mangled}\n    expected: {expected!r}\n    got:      {result!r}"
                )
    if xfails:
        print(f"xfail: {len(xfails)} known output differences")
    if failures:
        header = f"{len(failures)} of {total} demangle tests failed:\n"
        pytest.fail(header + "\n".join(failures))


# ---------------------------------------------------------------------------
# Basic API tests
# ---------------------------------------------------------------------------


class TestDemangleAPI:
    """Test the Python-level API contract."""

    def test_simple_function(self) -> None:
        assert pycxxfilt.demangle("_Z3fooi") == "foo(int)"

    def test_method(self) -> None:
        assert pycxxfilt.demangle("_ZN3Foo3barEv") == "Foo::bar()"

    def test_template(self) -> None:
        assert pycxxfilt.demangle("_Z1fIiEvT_") == "void f<int>(int)"

    def test_std_symbol(self) -> None:
        assert pycxxfilt.demangle("_ZSt4cout") == "std::cout"

    def test_invalid_returns_none(self) -> None:
        assert pycxxfilt.demangle("not_mangled") is None

    def test_plain_main_returns_none(self) -> None:
        assert pycxxfilt.demangle("main") is None

    def test_empty_string_returns_none(self) -> None:
        assert pycxxfilt.demangle("") is None

    def test_invalid_mangled_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="invalid mangled name"):
            pycxxfilt.demangle("_Zinvalid")

    def test_type_error_on_non_string(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.demangle(42)  # type: ignore[arg-type]

    def test_type_error_on_bytes(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.demangle(b"_Z3fooi")  # type: ignore[arg-type]

    def test_type_error_on_none(self) -> None:
        with pytest.raises(TypeError):
            pycxxfilt.demangle(None)  # type: ignore[arg-type]
