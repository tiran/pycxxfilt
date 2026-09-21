fs = import('fs')

llvm_inc = include_directories('../../vendor/llvm/include')

# Derive the demangler version from the vendored tag (llvmorg-23.1.0 -> 23.1.0);
# passed to the extension as a compile-time define, keeping LLVM_TAG canonical.
llvm_version = fs.read('../../vendor/LLVM_TAG').strip().split('llvmorg-')[1]

# All three engines (Itanium, MSVC, Rust) plus our extern "C" wrappers, from the
# llvm/ Demangle tree.  ItaniumDemangle.cpp provides itaniumDemangle() and
# OutputBuffer's vtable key functions, which the MSVC/Rust demanglers link
# against.  Built free of Python/limited-API flags so ccache can reuse it.
llvm_demangle = static_library('llvm_demangle',
    '../../vendor/llvm/lib/Demangle/ItaniumDemangle.cpp',
    '../../vendor/llvm/lib/Demangle/MicrosoftDemangle.cpp',
    '../../vendor/llvm/lib/Demangle/MicrosoftDemangleNodes.cpp',
    '../../vendor/llvm/lib/Demangle/RustDemangle.cpp',
    '_llvm_demangle.cpp',
    include_directories: llvm_inc,
    gnu_symbol_visibility: 'hidden',
    pic: true,
    install: false,
)

_cxxfilt = py.extension_module('_cxxfilt',
    sources: ['_cxxfilt.c'],
    c_args: ['-DPYCXXFILT_LLVM_VERSION="' + llvm_version + '"'],
    link_with: llvm_demangle,
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
