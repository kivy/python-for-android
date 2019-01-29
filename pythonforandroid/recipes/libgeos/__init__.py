from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh
from multiprocessing import cpu_count


class LibgeosRecipe(Recipe):
    version = '3.5'
    # url = 'http://download.osgeo.org/geos/geos-{version}.tar.bz2'
    url = 'https://github.com/libgeos/libgeos/archive/svn-{version}.zip'
    depends = []

    def should_build(self, arch):
        super(LibgeosRecipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libgeos_c.so'))

    def build_arch(self, arch):
        super(LibgeosRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            dst_dir = join(self.get_build_dir(arch.arch), 'dist')
            bash = sh.Command('bash')
            print("If this fails make sure you have autoconf and libtool installed")
            shprint(bash, 'autogen.sh')  # Requires autoconf and libtool
            shprint(bash, 'configure', '--host=arm-linux-androideabi', '--enable-shared', '--prefix={}'.format(dst_dir), _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)
            shutil.copyfile('{}/lib/libgeos_c.so'.format(dst_dir), join(self.ctx.get_libs_dir(arch.arch), 'libgeos_c.so'))

    def get_recipe_env(self, arch):
        env = super(LibgeosRecipe, self).get_recipe_env(arch)
        env['CXXFLAGS'] += ' -I{}/sources/cxx-stl/gnu-libstdc++/4.8/include'.format(self.ctx.ndk_dir)
        env['CXXFLAGS'] += ' -I{}/sources/cxx-stl/gnu-libstdc++/4.8/libs/{}/include'.format(
            self.ctx.ndk_dir, arch)
        env['CXXFLAGS'] += ' -L{}/sources/cxx-stl/gnu-libstdc++/4.8/libs/{}'.format(
            self.ctx.ndk_dir, arch)
        env['CXXFLAGS'] += ' -lgnustl_shared'
        env['LDFLAGS'] += ' -L{}/sources/cxx-stl/gnu-libstdc++/4.8/libs/{}'.format(
            self.ctx.ndk_dir, arch)
        return env


recipe = LibgeosRecipe()
