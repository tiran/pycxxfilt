project(
    'pycxxfilt',
    'c', 'cpp',
    version: '0.1.dev1',
    meson_version: '>=1.6.0',
    default_options: [
        'cpp_std=c++20',
        'b_ndebug=true',
    ],
)

cc = meson.get_compiler('c')

hardening_c_args = cc.get_supported_arguments(
    '-fstack-protector-strong',
    '-D_FORTIFY_SOURCE=2',
    '-fstack-clash-protection',
)
hardening_link_args = cc.get_supported_link_arguments(
    '-Wl,-z,relro',
    '-Wl,-z,now',
)
add_project_arguments(hardening_c_args, language: ['c', 'cpp'])
add_project_link_arguments(hardening_link_args, language: ['c', 'cpp'])

py = import('python').find_installation(pure: false)

subdir('src/pycxxfilt')
