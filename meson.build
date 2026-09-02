project(
    'pycxxfilt',
    'c', 'cpp',
    meson_version: '>=1.6.0',
    # Derive the version from the latest git tag via vcs-versioning. It falls
    # back to the sdist's PKG-INFO when building outside a git checkout.
    # find_program('python3') is special-cased by meson: when 'python3' is not
    # on PATH it falls back to meson's own interpreter, which under meson-python
    # is the build interpreter that carries the versioning deps.
    version: run_command(
        find_program('python3'), '-m', 'vcs_versioning',
        check: true,
    ).stdout().strip(),
    default_options: [
        'cpp_std=c++20',
        'b_ndebug=true',
        # Build version-specific extensions by default so plain source builds work
        # on every interpreter, including free-threaded ones (limited API is
        # unsupported there) and CPython 3.15+ (meson-python 0.20 chokes on its new
        # platform-tagged abi3 suffix). The distributed abi3 wheel opts back in with
        # -Dpython.allow_limited_api=true (see cibuildwheel cp311 override).
        'python.allow_limited_api=false',
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
