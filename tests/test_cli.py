# SPDX-License-Identifier: Apache-2.0
"""Tests for the ``python -m pycxxfilt`` CLI."""

from __future__ import annotations

import re
import subprocess
import sys

import pytest

import pycxxfilt
from pycxxfilt.__main__ import main


def test_llvm_version() -> None:
    assert isinstance(pycxxfilt.LLVM_VERSION, str)
    assert re.fullmatch(r"\d+\.\d+\.\d+", pycxxfilt.LLVM_VERSION), (
        pycxxfilt.LLVM_VERSION
    )


# ---------------------------------------------------------------------------
# Tests using main() directly
# ---------------------------------------------------------------------------


class TestMain:
    def test_single_symbol(self, capsys: pytest.CaptureFixture[str]) -> None:
        rc = main(["_Z3fooi"])
        assert rc == 0
        assert capsys.readouterr().out == "foo(int)\n"

    def test_multiple_symbols(self, capsys: pytest.CaptureFixture[str]) -> None:
        rc = main(["_Z3fooi", "_ZN3Foo3barEv", "_ZSt4cout"])
        assert rc == 0
        assert capsys.readouterr().out == "foo(int)\nFoo::bar()\nstd::cout\n"

    def test_invalid_symbol_passes_through(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        rc = main(["not_mangled"])
        assert rc == 0
        assert capsys.readouterr().out == "not_mangled\n"

    def test_mixed_valid_and_invalid(self, capsys: pytest.CaptureFixture[str]) -> None:
        rc = main(["_Z3fooi", "plain", "_ZN1A1BEv"])
        assert rc == 0
        out = capsys.readouterr().out
        assert out == "foo(int)\nplain\nA::B()\n"

    def test_no_args_returns_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        rc = main([])
        assert rc == 2
        assert "Usage:" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Tests via subprocess (python -m pycxxfilt)
# ---------------------------------------------------------------------------


class TestSubprocess:
    def test_module_invocation(self) -> None:
        r = subprocess.run(
            [sys.executable, "-m", "pycxxfilt", "_Z3fooi"],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0
        assert r.stdout.strip() == "foo(int)"

    def test_multiple_args(self) -> None:
        r = subprocess.run(
            [sys.executable, "-m", "pycxxfilt", "_Z3fooi", "_ZSt4cout"],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0
        assert r.stdout.strip().splitlines() == ["foo(int)", "std::cout"]

    def test_no_args_exit_code(self) -> None:
        r = subprocess.run(
            [sys.executable, "-m", "pycxxfilt"],
            capture_output=True,
            text=True,
        )
        assert r.returncode == 2
        assert "Usage:" in r.stderr
