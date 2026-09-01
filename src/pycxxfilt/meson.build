fs = import('fs')

vendor_inc = include_directories('../../vendor')

# Derive the demangler version from the vendored tag (llvmorg-23.1.0 -> 23.1.0);
# passed to the extension as a compile-time define, keeping LLVM_TAG canonical.
llvm_version = fs.read('../../vendor/LLVM_TAG').strip().split('llvmorg-')[1]

# Build the demangler separately, free of Python/limited-API flags, so ccache
# can reuse this expensive object across every interpreter build.
cxa_demangle = static_library('cxa_demangle',
    '../../vendor/cxa_demangle.cpp',
    include_directories: vendor_inc,
    gnu_symbol_visibility: 'hidden',
    pic: true,
    install: false,
)

_cxxfilt = py.extension_module('_cxxfilt',
    sources: ['_cxxfilt.c'],
    c_args: ['-DPYCXXFILT_LLVM_VERSION="' + llvm_version + '"'],
    link_with: cxa_demangle,
    gnu_symbol_visibility: 'hidden',
    link_language: 'cpp',
    limited_api: '3.11',
    install: true,
    subdir: 'pycxxfilt',
)

py.install_sources(
    '__init__.py',
    '__main__.py',
    '_cxxfilt.pyi',
    'py.typed',
    subdir: 'pycxxfilt',
)
