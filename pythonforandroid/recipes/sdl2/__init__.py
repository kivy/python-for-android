from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class LibSDL2Recipe(BootstrapNDKRecipe):
    version = "2.0.4"
    url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"
    md5sum = '44fc4a023349933e7f5d7a582f7b886e'

    dir_name = 'SDL'

    depends = [('python2', 'python3', 'python3crystax'), 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf']
    conflicts = ['sdl', 'pygame', 'pygame_bootstrap_components']

    patches = ['add_nativeSetEnv.patch']

    def get_recipe_env(self, arch=None):
        env = super(LibSDL2Recipe, self).get_recipe_env(arch)

        py2 = self.get_recipe('python2', arch.ctx)
        env['PYTHON2_NAME'] = py2.get_dir_name()

        env['PYTHON_INCLUDE_ROOT'] = self.ctx.python_recipe.include_root(arch.arch)
        env['PYTHON_LINK_ROOT'] = self.ctx.python_recipe.link_root(arch.arch)

        if 'python2' in self.ctx.recipe_build_order:
            env['EXTRA_LDLIBS'] = ' -lpython2.7'

        if 'python3' in self.ctx.recipe_build_order:
            env['EXTRA_LDLIBS'] = ' -lpython{}m'.format(
                self.ctx.python_recipe.major_minor_version_string)

        env['APP_ALLOW_MISSING_DEPS'] = 'true'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = LibSDL2Recipe()
