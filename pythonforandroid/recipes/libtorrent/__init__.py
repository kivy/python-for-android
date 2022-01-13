from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from multiprocessing import cpu_count
from os.path import join, basename
from os import listdir, walk
import sh

# This recipe builds libtorrent with Python bindings
# It depends on Boost.Build and the source of several Boost libraries present
# in BOOST_ROOT, which is all provided by the boost recipe


def get_lib_from(search_directory, lib_extension='.so'):
    '''Scan directories recursively until find any file with the given
    extension. The default extension to search is ``.so``.'''
    for root, dirs, files in walk(search_directory):
        for file in files:
            if file.endswith(lib_extension):
                print('get_lib_from: {}\n\t- {}'.format(
                    search_directory, join(root, file)))
                return join(root, file)
    return None


class LibtorrentRecipe(Recipe):
    # Todo: make recipe compatible with all p4a architectures
    '''
    .. note:: This recipe can be built only against API 21+ and an android
              ndk >= r19

    .. versionchanged:: 0.6.0
         Rewrote recipe to support clang's build and boost 1.68. The following
         changes has been made:

            - Bumped version number to 1.2.0
            - added python 3 compatibility
            - new system to detect/copy generated libraries

    .. versionchanged:: 2019.08.09.1.dev0

            - Bumped version number to 1.2.1
            - Adapted to work with ndk-r19+
    '''
    version = '1_2_1'
    url = 'https://github.com/arvidn/libtorrent/archive/libtorrent-{version}.tar.gz'

    depends = ['boost']
    opt_depends = ['openssl']
    patches = ['disable-so-version.patch',
               'use-soname-python.patch',
               'setup-lib-name.patch']

    # libtorrent.so is not included because is not a system library
    generated_libraries = [
        'boost_system', 'boost_python{py_version}', 'torrent_rasterbar']

    def should_build(self, arch):
        python_version = self.ctx.python_recipe.version[:3].replace('.', '')
        libs = ['lib' + lib_name.format(py_version=python_version) +
                '.so' for lib_name in self.generated_libraries]
        return not (self.has_libs(arch, *libs) and
                    self.ctx.has_package('libtorrent', arch.arch))

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        if 'openssl' in recipe.ctx.recipe_build_order:
            # Patch boost user-config.jam to use openssl
            self.get_recipe('boost', self.ctx).apply_patch(
                join(self.get_recipe_dir(), 'user-config-openssl.patch'), arch.arch)

    def build_arch(self, arch):
        super().build_arch(arch)
        env = self.get_recipe_env(arch)
        env['PYTHON_HOST'] = self.ctx.hostpython

        # Define build variables
        build_dir = self.get_build_dir(arch.arch)
        ctx_libs_dir = self.ctx.get_libs_dir(arch.arch)
        encryption = 'openssl' if 'openssl' in recipe.ctx.recipe_build_order else 'built-in'
        build_args = [
            '-q',
            # '-a',  # force build, useful to debug the build
            '-j' + str(cpu_count()),
            '--debug-configuration',  # so we know if our python is detected
            # '--deprecated-functions=off',
            'toolset=clang-{arch}'.format(arch=env['ARCH']),
            'abi=aapcs',
            'binary-format=elf',
            'cxxflags=-std=c++11',
            'target-os=android',
            'threading=multi',
            'link=shared',
            'boost-link=shared',
            'libtorrent-link=shared',
            'runtime-link=shared',
            'encryption={}'.format('on' if encryption == 'openssl' else 'off'),
            'crypto=' + encryption
        ]
        crypto_folder = 'encryption-off'
        if encryption == 'openssl':
            crypto_folder = 'crypto-openssl'
            build_args.extend(['openssl-lib=' + env['OPENSSL_BUILD_PATH'],
                               'openssl-include=' + env['OPENSSL_INCLUDE']
                               ])
        build_args.append('release')

        # Compile libtorrent with boost libraries and python bindings
        with current_directory(join(build_dir, 'bindings/python')):
            b2 = sh.Command(join(env['BOOST_ROOT'], 'b2'))
            shprint(b2, *build_args, _env=env)

        # Copy only the boost shared libraries into the libs folder. Because
        # boost build two boost_python libraries, we force to search the lib
        # into the corresponding build path.
        b2_build_dir = (
            'build/clang-linux-{arch}/release/{encryption}/'
            'lt-visibility-hidden/'.format(
                arch=env['ARCH'], encryption=crypto_folder
            )
        )
        boost_libs_dir = join(env['BOOST_BUILD_PATH'], 'bin.v2/libs')
        for boost_lib in listdir(boost_libs_dir):
            lib_path = get_lib_from(join(boost_libs_dir, boost_lib, b2_build_dir))
            if lib_path:
                lib_name = basename(lib_path)
                shutil.copyfile(lib_path, join(ctx_libs_dir, lib_name))

        # Copy libtorrent shared libraries into the right places
        system_libtorrent = get_lib_from(join(build_dir, 'bin'))
        if system_libtorrent:
            shutil.copyfile(system_libtorrent,
                            join(ctx_libs_dir, 'libtorrent_rasterbar.so'))

        python_libtorrent = get_lib_from(join(build_dir, 'bindings/python/bin'))
        shutil.copyfile(python_libtorrent,
                        join(self.ctx.get_site_packages_dir(arch), 'libtorrent.so'))

    def get_recipe_env(self, arch):
        # Use environment from boost recipe, cause we use b2 tool from boost
        env = self.get_recipe('boost', self.ctx).get_recipe_env(arch)
        if 'openssl' in recipe.ctx.recipe_build_order:
            r = self.get_recipe('openssl', self.ctx)
            env['OPENSSL_BUILD_PATH'] = r.get_build_dir(arch.arch)
            env['OPENSSL_INCLUDE'] = join(r.get_build_dir(arch.arch), 'include')
            env['OPENSSL_VERSION'] = r.version
        return env


recipe = LibtorrentRecipe()
