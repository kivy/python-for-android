from distutils.spawn import find_executable
from os import environ
from os.path import join
from multiprocessing import cpu_count

from pythonforandroid.recipe import Recipe
from pythonforandroid.util import BuildInterruptingException, build_platform


class Arch:

    command_prefix = None
    '''The prefix for NDK commands such as gcc.'''

    arch = ""
    '''Name of the arch such as: `armeabi-v7a`, `arm64-v8a`, `x86`...'''

    arch_cflags = []
    '''Specific arch `cflags`, expect to be overwrote in subclass if needed.'''

    common_cflags = [
        '-target {target}',
        '-fomit-frame-pointer'
    ]

    common_cppflags = [
        '-DANDROID',
        '-I{ctx.ndk.sysroot_include_dir}',
        '-I{python_includes}',
    ]

    common_ldflags = ['-L{ctx_libs_dir}']

    common_ldlibs = ['-lm']

    common_ldshared = [
        '-pthread',
        '-shared',
        '-Wl,-O1',
        '-Wl,-Bsymbolic-functions',
    ]

    def __init__(self, ctx):
        self.ctx = ctx

        # Allows injecting additional linker paths used by any recipe.
        # This can also be modified by recipes (like the librt recipe)
        # to make sure that some sort of global resource is available &
        # linked for all others.
        self.extra_global_link_paths = []

    def __str__(self):
        return self.arch

    @property
    def ndk_lib_dir(self):
        return join(self.ctx.ndk.sysroot_lib_dir, self.command_prefix)

    @property
    def ndk_lib_dir_versioned(self):
        return join(self.ndk_lib_dir, str(self.ctx.ndk_api))

    @property
    def include_dirs(self):
        return [
            "{}/{}".format(
                self.ctx.include_dir,
                d.format(arch=self))
            for d in self.ctx.include_dirs]

    @property
    def target(self):
        # As of NDK r19, the toolchains installed by default with the
        # NDK may be used in-place. The make_standalone_toolchain.py script
        # is no longer needed for interfacing with arbitrary build systems.
        # See: https://developer.android.com/ndk/guides/other_build_systems
        return '{triplet}{ndk_api}'.format(
            triplet=self.command_prefix, ndk_api=self.ctx.ndk_api
        )

    @property
    def clang_exe(self):
        """Full path of the clang compiler depending on the android's ndk
        version used."""
        return self.get_clang_exe()

    @property
    def clang_exe_cxx(self):
        """Full path of the clang++ compiler depending on the android's ndk
        version used."""
        return self.get_clang_exe(plus_plus=True)

    def get_clang_exe(self, with_target=False, plus_plus=False):
        """Returns the full path of the clang/clang++ compiler, supports two
        kwargs:

          - `with_target`: prepend `target` to clang
          - `plus_plus`: will return the clang++ compiler (defaults to `False`)
        """
        compiler = 'clang'
        if with_target:
            compiler = '{target}-{compiler}'.format(
                target=self.target, compiler=compiler
            )
        if plus_plus:
            compiler += '++'
        return join(self.ctx.ndk.llvm_bin_dir, compiler)

    def get_env(self, with_flags_in_cc=True):
        env = {}

        # CFLAGS/CXXFLAGS: the processor flags
        env['CFLAGS'] = ' '.join(self.common_cflags).format(target=self.target)
        if self.arch_cflags:
            # each architecture may have has his own CFLAGS
            env['CFLAGS'] += ' ' + ' '.join(self.arch_cflags)
        env['CXXFLAGS'] = env['CFLAGS']

        # CPPFLAGS (for macros and includes)
        env['CPPFLAGS'] = ' '.join(self.common_cppflags).format(
            ctx=self.ctx,
            command_prefix=self.command_prefix,
            python_includes=join(
                self.ctx.get_python_install_dir(self.arch),
                'include/python{}'.format(self.ctx.python_recipe.version[0:3]),
            ),
        )

        # LDFLAGS: Link the extra global link paths first before anything else
        # (such that overriding system libraries with them is possible)
        env['LDFLAGS'] = (
            ' '
            + " ".join(
                [
                    "-L'"
                    + link_path.replace("'", "'\"'\"'")
                    + "'"  # no shlex.quote in py2
                    for link_path in self.extra_global_link_paths
                ]
            )
            + ' ' + ' '.join(self.common_ldflags).format(
                ctx_libs_dir=self.ctx.get_libs_dir(self.arch)
            )
        )

        # LDLIBS: Library flags or names given to compilers when they are
        # supposed to invoke the linker.
        env['LDLIBS'] = ' '.join(self.common_ldlibs)

        # CCACHE
        ccache = ''
        if self.ctx.ccache and bool(int(environ.get('USE_CCACHE', '1'))):
            # print('ccache found, will optimize builds')
            ccache = self.ctx.ccache + ' '
            env['USE_CCACHE'] = '1'
            env['NDK_CCACHE'] = self.ctx.ccache
            env.update(
                {k: v for k, v in environ.items() if k.startswith('CCACHE_')}
            )

        # Compiler: `CC` and `CXX` (and make sure that the compiler exists)
        env['PATH'] = self.ctx.env['PATH']
        cc = find_executable(self.clang_exe, path=env['PATH'])
        if cc is None:
            print('Searching path are: {!r}'.format(env['PATH']))
            raise BuildInterruptingException(
                'Couldn\'t find executable for CC. This indicates a '
                'problem locating the {} executable in the Android '
                'NDK, not that you don\'t have a normal compiler '
                'installed. Exiting.'.format(self.clang_exe))

        if with_flags_in_cc:
            env['CC'] = '{ccache}{exe} {cflags}'.format(
                exe=self.clang_exe,
                ccache=ccache,
                cflags=env['CFLAGS'])
            env['CXX'] = '{ccache}{execxx} {cxxflags}'.format(
                execxx=self.clang_exe_cxx,
                ccache=ccache,
                cxxflags=env['CXXFLAGS'])
        else:
            env['CC'] = '{ccache}{exe}'.format(
                exe=self.clang_exe,
                ccache=ccache)
            env['CXX'] = '{ccache}{execxx}'.format(
                execxx=self.clang_exe_cxx,
                ccache=ccache)

        # Android's LLVM binutils
        env['AR'] = self.ctx.ndk.llvm_ar
        env['RANLIB'] = self.ctx.ndk.llvm_ranlib
        env['STRIP'] = f'{self.ctx.ndk.llvm_strip} --strip-unneeded'
        env['READELF'] = self.ctx.ndk.llvm_readelf
        env['OBJCOPY'] = self.ctx.ndk.llvm_objcopy

        env['MAKE'] = 'make -j{}'.format(str(cpu_count()))

        # Android's arch/toolchain
        env['ARCH'] = self.arch
        env['NDK_API'] = 'android-{}'.format(str(self.ctx.ndk_api))

        # Custom linker options
        env['LDSHARED'] = env['CC'] + ' ' + ' '.join(self.common_ldshared)

        # Host python (used by some recipes)
        hostpython_recipe = Recipe.get_recipe(
            'host' + self.ctx.python_recipe.name, self.ctx)
        env['BUILDLIB_PATH'] = join(
            hostpython_recipe.get_build_dir(self.arch),
            'native-build',
            'build',
            'lib.{}-{}'.format(
                build_platform,
                self.ctx.python_recipe.major_minor_version_string,
            ),
        )

        # for reproducible builds
        if 'SOURCE_DATE_EPOCH' in environ:
            for k in 'LC_ALL TZ SOURCE_DATE_EPOCH PYTHONHASHSEED BUILD_DATE BUILD_TIME'.split():
                if k in environ:
                    env[k] = environ[k]

        return env


class ArchARM(Arch):
    arch = "armeabi"
    command_prefix = 'arm-linux-androideabi'

    @property
    def target(self):
        target_data = self.command_prefix.split('-')
        return '{triplet}{ndk_api}'.format(
            triplet='-'.join(['armv7a', target_data[1], target_data[2]]),
            ndk_api=self.ctx.ndk_api,
        )


class ArchARMv7_a(ArchARM):
    arch = 'armeabi-v7a'
    arch_cflags = [
        '-march=armv7-a',
        '-mfloat-abi=softfp',
        '-mfpu=vfp',
        '-mthumb',
        '-fPIC',
    ]


class Archx86(Arch):
    arch = 'x86'
    command_prefix = 'i686-linux-android'
    arch_cflags = [
        '-march=i686',
        '-mssse3',
        '-mfpmath=sse',
        '-m32',
        '-fPIC',
    ]


class Archx86_64(Arch):
    arch = 'x86_64'
    command_prefix = 'x86_64-linux-android'
    arch_cflags = [
        '-march=x86-64',
        '-msse4.2',
        '-mpopcnt',
        '-m64',
        '-fPIC',
    ]


class ArchAarch_64(Arch):
    arch = 'arm64-v8a'
    command_prefix = 'aarch64-linux-android'
    arch_cflags = [
        '-march=armv8-a',
        '-fPIC'
        # '-I' + join(dirname(__file__), 'includes', 'arm64-v8a'),
    ]

    # Note: This `EXTRA_CFLAGS` below should target the commented `include`
    # above in `arch_cflags`. The original lines were added during the Sdl2's
    # bootstrap creation, and modified/commented during the migration to the
    # NDK r19 build system, because it seems that we don't need it anymore,
    # do we need them?
    # def get_env(self, with_flags_in_cc=True):
    #     env = super().get_env(with_flags_in_cc)
    #     env['EXTRA_CFLAGS'] = self.arch_cflags[-1]
    #     return env
