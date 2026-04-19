# SPDX-License-Identifier: Apache-2.0
"""Shared fixtures and test-case loading for pycxxfilt tests.

Test cases are parsed from vendor/DemangleTestCases.inc which is copied
unmodified from libcxxabi/test/DemangleTestCases.inc (llvmorg-22.1.3).
The file contains ~30 000 mangled/demangled pairs in C array-initializer
syntax::

    {"_Z1A", "A"},
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

# Pattern matches: {"mangled", "demangled"},
# Handles escaped characters inside the C string literals.
_PAIR_RE = re.compile(r'\{"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\}')

_VENDOR_DIR = Path(__file__).resolve().parent.parent / "vendor"


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
    inc_file = _VENDOR_DIR / "DemangleTestCases.inc"
    for line in inc_file.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("//"):
            continue
        m = _PAIR_RE.search(line)
        if m:
            mangled = _unescape_c_string(m.group(1))
            expected = _unescape_c_string(m.group(2))
            yield (mangled, expected)
