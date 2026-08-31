vendor_inc = include_directories('../../vendor')

_cxxfilt = py.extension_module('_cxxfilt',
    sources: [
        '_cxxfilt.c',
        '../../vendor/cxa_demangle.cpp',
    ],
    include_directories: vendor_inc,
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
