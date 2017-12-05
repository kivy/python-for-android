from pythonforandroid.toolchain import BootstrapNDKRecipe, shprint, current_directory, info
from os.path import exists, join
import sh


class GenericNDKBuildRecipe(BootstrapNDKRecipe):
    version = None
    url = None

    depends = [('python2', 'python3crystax')]
    conflicts = ['sdl2', 'pygame', 'sdl']

    def should_build(self, arch):
        return True

    def get_recipe_env(self, arch=None):
        env = super(GenericNDKBuildRecipe, self).get_recipe_env(arch)
        py2 = self.get_recipe('python2', arch.ctx)
        env['PYTHON2_NAME'] = py2.get_dir_name()
        if 'python2' in self.ctx.recipe_build_order:
            env['EXTRA_LDLIBS'] = ' -lpython2.7'

        env['APP_ALLOW_MISSING_DEPS'] = 'true'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = GenericNDKBuildRecipe()
