from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
from os.path import join
import sh


class OggRecipe(NDKRecipe):
    version = '1.3.3'
    url = 'http://downloads.xiph.org/releases/ogg/libogg-{version}.tar.gz'

    generated_libraries = ['libogg.so']

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            flags = [
                '--with-sysroot=' + self.ctx.ndk_platform,
                '--host=' + arch.toolchain_prefix,
            ]
            configure = sh.Command('./configure')
            shprint(configure, *flags, _env=env)
            shprint(sh.make, _env=env)
            self.install_libs(arch, join('src', '.libs', 'libogg.so'))


recipe = OggRecipe()
