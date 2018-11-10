from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh


class LibsodiumRecipe(Recipe):
    version = '1.0.16'
    url = 'https://github.com/jedisct1/libsodium/releases/download/{version}/libsodium-{version}.tar.gz'
    depends = ['python2']
    patches = ['size_max_fix.patch']

    def should_build(self, arch):
        super(LibsodiumRecipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libsodium.so'))

    def build_arch(self, arch):
        super(LibsodiumRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            bash = sh.Command('bash')
            shprint(bash, 'configure', '--disable-soname-versions', '--host=arm-linux-androideabi', '--enable-shared', _env=env)
            shprint(sh.make, _env=env)
            shutil.copyfile('src/libsodium/.libs/libsodium.so', join(self.ctx.get_libs_dir(arch.arch), 'libsodium.so'))

    def get_recipe_env(self, arch):
        env = super(LibsodiumRecipe, self).get_recipe_env(arch)
        env['CFLAGS'] += ' -Os'
        return env


recipe = LibsodiumRecipe()
