vendor_inc = include_directories('../../vendor')

# Build the vendored demangler separately, free of Python/limited-API flags, so
# ccache can reuse this expensive object across every interpreter build.
cxa_demangle = static_library('cxa_demangle',
    '../../vendor/cxa_demangle.cpp',
    include_directories: vendor_inc,
    gnu_symbol_visibility: 'hidden',
    pic: true,
    install: false,
)

_cxxfilt = py.extension_module('_cxxfilt',
    sources: ['_cxxfilt.c'],
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
