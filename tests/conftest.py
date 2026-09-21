# SPDX-License-Identifier: Apache-2.0
"""Shared fixtures and test-case loading for pycxxfilt tests.

All vendored corpora live under vendor/test/ (see vendor/LLVM_TAG for the
release):

* ``DemangleTestCases.inc`` -- ~30 000 Itanium mangled/demangled pairs from
  libcxxabi, in C array-initializer syntax (``{"_Z1A", "A"},``).
* ``ms-*.test`` / ``rust.test`` -- LLVM's FileCheck-based lit tests for the
  MSVC and Rust demanglers, parsed here with FileCheck's matching semantics.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

# Pattern matches: {"mangled", "demangled"},
# Handles escaped characters inside the C string literals.
_PAIR_RE = re.compile(r'\{"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\}')

_TEST_DIR = Path(__file__).resolve().parent.parent / "vendor" / "test"


_SIMPLE_ESCAPES: dict[str, str] = {
    "\\": "\\",
    '"': '"',
    "'": "'",
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "0": "\0",
}

_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_OCT_DIGITS = frozenset("01234567")


def _unescape_c_string(s: str) -> str:
    """Process C string escape sequences (simple, hex, and octal)."""
    result: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            if c in _SIMPLE_ESCAPES:
                result.append(_SIMPLE_ESCAPES[c])
                i += 2
            elif c == "x":
                # Hex escape: \xHH (1-2 hex digits)
                j = i + 2
                while j < len(s) and j - i - 2 < 2 and s[j] in _HEX_DIGITS:
                    j += 1
                result.append(chr(int(s[i + 2 : j], 16)))
                i = j
            elif c in _OCT_DIGITS:
                # Octal escape: \OOO (1-3 octal digits)
                j = i + 1
                while j < len(s) and j - i - 1 < 3 and s[j] in _OCT_DIGITS:
                    j += 1
                result.append(chr(int(s[i + 1 : j], 8)))
                i = j
            else:
                # Unknown escape -- keep as-is
                result.append(s[i : i + 2])
                i += 2
        else:
            result.append(s[i])
            i += 1
    return "".join(result)


def iter_demangle_test_cases() -> Iterator[tuple[str, str]]:
    """Yield (mangled, expected) pairs from DemangleTestCases.inc."""
    inc_file = _TEST_DIR / "DemangleTestCases.inc"
    for line in inc_file.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("//"):
            continue
        m = _PAIR_RE.search(line)
        if m:
            mangled = _unescape_c_string(m.group(1))
            expected = _unescape_c_string(m.group(2))
            yield (mangled, expected)


def canonicalize_ws(s: str) -> str:
    """Collapse whitespace runs to a single space and strip.

    Mirrors FileCheck's default whitespace canonicalization, so vendored
    ``.test`` expectations compare equal regardless of spacing.
    """
    return " ".join(s.split())


def iter_msvc_test_cases() -> Iterator[tuple[str, str, str]]:
    """Yield (mangled, expected, source) from the vendored ms-*.test files.

    Each ``?...`` input line is paired with the following ``; CHECK:`` line.
    FileCheck treats that text as a whitespace-canonicalized *substring* of
    llvm-undname's output; ``CHECK-NOT`` / ``CHECK-NEXT`` lines are ignored.
    """
    for path in sorted(_TEST_DIR.glob("ms-*.test")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if not line.startswith("?"):
                continue
            for nxt in lines[i + 1 :]:
                stripped = nxt.strip()
                if not stripped:
                    continue
                if stripped.startswith("; CHECK:"):
                    expected = stripped[len("; CHECK:") :].strip()
                    yield (line, expected, path.name)
                break


def iter_rust_test_cases() -> Iterator[tuple[str, str]]:
    """Yield (mangled, expected) from the vendored rust.test file.

    Each ``CHECK:`` line holds the full expected output (--match-full-lines)
    for the ``_R...`` name on the following line.  Invalid manglings pass
    through llvm-cxxfilt unchanged, so expected == mangled marks a case where
    our rust_demangle returns None.
    """
    lines = (_TEST_DIR / "rust.test").read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("CHECK:"):
            continue
        expected = stripped[len("CHECK:") :].strip()
        for nxt in lines[i + 1 :]:
            mangled = nxt.strip()
            if mangled and not mangled.startswith(("CHECK", ";")):
                yield (mangled, expected)
                break
