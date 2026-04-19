<!-- SPDX-License-Identifier: Apache-2.0 -->
# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities privately via
[GitHub Security Advisories](https://github.com/tiran/pycxxfilt/security/advisories/new).

Do **not** open a public issue for security-related bugs.

## Scope

pycxxfilt wraps LLVM's Itanium C++ name demangler. Security-relevant
issues include:

- Memory safety bugs in the C extension or vendored LLVM code
- Denial of service via crafted mangled names (excessive CPU or memory)
- Build system or supply chain issues

## Vendored Code

The demangler is vendored from LLVM's libcxxabi. If a vulnerability is
found in the upstream LLVM code, please also report it to the
[LLVM project](https://llvm.org/docs/Security.html).
