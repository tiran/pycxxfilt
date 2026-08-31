#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assert that the built wheels carry exactly the intended ABI tags.

Run against the collected wheelhouse, e.g.::

    python3 .github/check-wheel-tags.py wheelhouse/*.whl

Wheel filenames follow ``{name}-{version}-{pytag}-{abitag}-{platform}.whl``.
``MUST_BUILD`` below is the hard-coded list of ``{pytag}-{abitag}`` suffixes we
ship. The check fails if any built wheel has a suffix not in the list, or if any
listed suffix is missing for a target that was built.

Completeness is checked per ``os-arch`` family rather than per raw platform tag:
a single architecture legitimately produces several platform tags (macOS wheels
carry the build interpreter's deployment target, so cp311 and cp314 differ; the
glibc and musl Linux variants differ too), and demanding every ABI under each
individual tag would spuriously fail.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

# Architectures recognised inside platform tags, checked longest-first so that
# e.g. "x86_64" wins before a shorter substring could match.
_ARCHES = ("x86_64", "aarch64", "ppc64le", "s390x", "arm64", "amd64", "i686")


def platform_family(platform: str) -> str:
    """Collapse a wheel platform tag to an ``os-arch`` family key."""
    if "macosx" in platform:
        os_ = "macos"
    elif "linux" in platform:  # manylinux / musllinux / linux
        os_ = "linux"
    elif platform.startswith("win"):
        os_ = "windows"
    else:
        os_ = platform
    arch = next((a for a in _ARCHES if a in platform), platform)
    return f"{os_}-{arch}"

# Wheel ABI suffixes ({python-tag}-{abi-tag}) that MUST be built for every
# platform. Every built wheel must match one of these exactly.
MUST_BUILD = [
    "cp311-abi3",    # stable ABI: one wheel covers every GIL build 3.11+
    "cp314-cp314t",  # free-threaded 3.14 (no stable ABI for FT before 3.15)
    # PEP 803 abi3.abi3t: single wheel for 3.15+ GIL *and* free-threaded.
    # Uncomment once meson-python ships abi3t support and "cp315t-*" is added
    # to [tool.cibuildwheel] build in pyproject.toml.
    # "cp315-abi3.abi3t",
]


def main(paths: list[str]) -> int:
    wheels = [Path(p) for p in paths]
    if not wheels:
        print("error: no wheels to check", file=sys.stderr)
        return 1

    required = set(MUST_BUILD)
    ok = True
    suffixes_by_family: dict[str, set[str]] = defaultdict(set)

    for wheel in wheels:
        # Split from the right: platform, abi, python are the last three fields
        # (an optional build-number field sits further left and is ignored).
        parts = wheel.stem.split("-")
        if len(parts) < 5:
            print(f"FAIL  {wheel.name}: cannot parse wheel tags")
            ok = False
            continue

        pytag, abitag, platform = parts[-3], parts[-2], parts[-1]
        suffix = f"{pytag}-{abitag}"
        suffixes_by_family[platform_family(platform)].add(suffix)

        if suffix in required:
            print(f"OK    {wheel.name}: {suffix}")
        else:
            print(f"FAIL  {wheel.name}: unexpected suffix {suffix}")
            ok = False

    for family, built in sorted(suffixes_by_family.items()):
        missing = required - built
        if missing:
            print(f"FAIL  {family}: missing required wheels {sorted(missing)}")
            ok = False

    print("\nall wheel tags OK" if ok else "\nwheel tag check FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
