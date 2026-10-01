# SPDX-License-Identifier: Apache-2.0
"""Tests for pycxxfilt.demangle().

The bulk of the test cases come from LLVM's DemangleTestCases.inc
(libcxxabi/test/DemangleTestCases.inc; see vendor/LLVM_TAG for the
release) which contains ~30 000 mangled/demangled pairs.
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
    assert total > 1000, f"Itanium corpus not loaded (got {total} cases)"
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
        with pytest.raises(ValueError, match="invalid Itanium mangled name"):
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


class TestAutoDispatch:
    """demangle() routes to the right engine by prefix."""

    def test_itanium(self) -> None:
        assert pycxxfilt.demangle("_Z3fooi") == "foo(int)"

    def test_microsoft(self) -> None:
        assert (
            pycxxfilt.demangle("?foo@Tensor@at@@QEAAXXZ")
            == "public: void __cdecl at::Tensor::foo(void)"
        )

    def test_rust(self) -> None:
        assert pycxxfilt.demangle("_RNvC6_123foo3bar") == "123foo::bar"

    def test_microsoft_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid MSVC mangled name"):
            pycxxfilt.demangle("?bad")

    def test_rust_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid Rust mangled name"):
            pycxxfilt.demangle("_Rbad")

    def test_rust_prefix_beats_itanium(self) -> None:
        # "_R" dispatches to Rust, never Itanium.
        assert pycxxfilt.demangle("_RNvC1a4main") == "a::main"


class TestItaniumSymbolVersion:
    """GNU symbol versions (name@VER / name@@VER) on the Itanium path."""

    @pytest.mark.parametrize(
        ("mangled", "expected"),
        [
            ("_Z3fooi@@GLIBCXX_3.4", "foo(int)@@GLIBCXX_3.4"),
            ("_Z3fooi@GLIBCXX_3.4", "foo(int)@GLIBCXX_3.4"),
            (
                "_ZNKSs11_M_disjunctEPKc@@GLIBCXX_3.4.5",
                "std::string::_M_disjunct(char const*) const@@GLIBCXX_3.4.5",
            ),
            # "@" is structural in MSVC names; it must not be split off.
            (
                "?foo@Tensor@at@@QEAAXXZ",
                "public: void __cdecl at::Tensor::foo(void)",
            ),
        ],
    )
    def test_versioned(self, mangled: str, expected: str) -> None:
        assert pycxxfilt.demangle(mangled) == expected

    def test_invalid_mangled_with_version_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid Itanium mangled name"):
            pycxxfilt.demangle("_Zinvalid@@VER")

    def test_non_mangled_with_version_returns_none(self) -> None:
        assert pycxxfilt.demangle("plain@thing") is None

    @pytest.mark.parametrize(
        "mangled",
        ["_Z3fooi@@GLIBCXX_3.4", "_Z3fooi@GLIBCXX_3.4"],
    )
    def test_primitive_rejects_version(self, mangled: str) -> None:
        # Version stripping lives in demangle(); itanium_demangle() is strict.
        with pytest.raises(ValueError, match="invalid Itanium mangled name"):
            pycxxfilt.itanium_demangle(mangled)
