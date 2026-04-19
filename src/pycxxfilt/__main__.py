# SPDX-License-Identifier: Apache-2.0
"""CLI entry point: ``python -m pycxxfilt SYMBOL [SYMBOL ...]``."""

from __future__ import annotations

import sys

from pycxxfilt import demangle


def main(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]

    if not args:
        print(f"Usage: {sys.argv[0]} SYMBOL [SYMBOL ...]", file=sys.stderr)
        return 2

    for mangled in args:
        result = demangle(mangled)
        print(result if result is not None else mangled)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
