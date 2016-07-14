from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import join, exists
import sh

# This recipe builds libtorrent with Python bindings
# It depends on Boost.Build and the source of several Boost libraries present in BOOST_ROOT,
# which is all provided by the boost recipe
class LibtorrentRecipe(Recipe):
    version = '1.0.9'
    # Don't forget to change the URL when changing the version
    url = 'https://github.com/arvidn/libtorrent/archive/libtorrent-1_0_9.tar.gz'
    depends = ['boost', 'python2']
    opt_depends = ['openssl']
    patches = ['disable-so-version.patch', 'use-soname-python.patch', 'setup-lib-name.patch']

    def should_build(self, arch):
        return not ( self.has_libs(arch, 'libboost_python.so', 'libboost_system.so', 'libtorrent_rasterbar.so')
                     and self.ctx.has_package('libtorrent', arch.arch) )

    def prebuild_arch(self, arch):
        super(LibtorrentRecipe, self).prebuild_arch(arch)
        if 'openssl' in recipe.ctx.recipe_build_order:
            # Patch boost user-config.jam to use openssl
            self.get_recipe('boost', self.ctx).apply_patch(join(self.get_recipe_dir(), 'user-config-openssl.patch'), arch.arch)

    def build_arch(self, arch):
        super(LibtorrentRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(join(self.get_build_dir(arch.arch), 'bindings/python')):
            # Compile libtorrent with boost libraries and python bindings
            b2 = sh.Command(join(env['BOOST_ROOT'], 'b2'))
            shprint(b2,
                    '-q',
                    '-j5',
                    'toolset=gcc-' + env['ARCH'],
                    'target-os=android',
                    'threading=multi',
                    'link=shared',
                    'boost-link=shared',
                    'boost=source',
                    'encryption=openssl' if 'openssl' in recipe.ctx.recipe_build_order else '',
                    '--prefix=' + env['CROSSHOME'],
                    'release'
            , _env=env)
        # Common build directories
        build_subdirs = 'gcc-arm/release/boost-link-shared/boost-source'
        if 'openssl' in recipe.ctx.recipe_build_order:
            build_subdirs += '/encryption-openssl'
        build_subdirs += '/libtorrent-python-pic-on/target-os-android/threading-multi/visibility-hidden'
        # Copy the shared libraries into the libs folder
        shutil.copyfile(join(env['BOOST_BUILD_PATH'], 'bin.v2/libs/python/build', build_subdirs, 'libboost_python.so'),
                        join(self.ctx.get_libs_dir(arch.arch), 'libboost_python.so'))
        shutil.copyfile(join(env['BOOST_BUILD_PATH'], 'bin.v2/libs/system/build', build_subdirs, 'libboost_system.so'),
                        join(self.ctx.get_libs_dir(arch.arch), 'libboost_system.so'))
        if 'openssl' in recipe.ctx.recipe_build_order:
            shutil.copyfile(join(env['BOOST_BUILD_PATH'], 'bin.v2/libs/date_time/build', build_subdirs, 'libboost_date_time.so'),
                        join(self.ctx.get_libs_dir(arch.arch), 'libboost_date_time.so'))
        shutil.copyfile(join(self.get_build_dir(arch.arch), 'bin', build_subdirs, 'libtorrent_rasterbar.so'),
                        join(self.ctx.get_libs_dir(arch.arch), 'libtorrent_rasterbar.so'))
        shutil.copyfile(join(self.get_build_dir(arch.arch), 'bindings/python/bin', build_subdirs, 'libtorrent.so'),
                        join(self.ctx.get_site_packages_dir(arch.arch), 'libtorrent.so'))

    def get_recipe_env(self, arch):
        env = super(LibtorrentRecipe, self).get_recipe_env(arch)
        # Copy environment from boost recipe
        env.update(self.get_recipe('boost', self.ctx).get_recipe_env(arch))
        if 'openssl' in recipe.ctx.recipe_build_order:
            r = self.get_recipe('openssl', self.ctx)
            env['OPENSSL_BUILD_PATH'] = r.get_build_dir(arch.arch)
            env['OPENSSL_VERSION'] = r.version
        return env

recipe = LibtorrentRecipe()
