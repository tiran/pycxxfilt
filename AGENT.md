# SPDX-License-Identifier: Apache-2.0

# Agent instructions

## Setup

Use [uv](https://docs.astral.sh/uv/) to create a venv and install
dependencies:

```
uv venv .venv && source .venv/bin/activate
uv pip install meson-python meson
uv pip install --no-build-isolation -e ".[test]"
```

## Testing

Run the test suite with pytest:

```
python -m pytest tests/ -q
```

## tox

Use tox for the full CI matrix (lint, typecheck, tests across Python
versions):

```
tox run                 # all environments
tox run -e lint         # ruff check + format check
tox run -e fix          # ruff auto-fix + format
tox run -e typecheck    # ty type checker
tox run -e py314        # tests with specific Python version
```
