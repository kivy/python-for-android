from os.path import join

from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class GenericNDKBuildRecipe(BootstrapNDKRecipe):
    version = None
    url = None

    depends = ['python3']
    conflicts = ['sdl2']

    def should_build(self, arch):
        return True

    def get_recipe_env(self, arch=None, with_flags_in_cc=True, with_python=True):
        env = super().get_recipe_env(
            arch=arch, with_flags_in_cc=with_flags_in_cc,
            with_python=with_python,
        )
        env['APP_ALLOW_MISSING_DEPS'] = 'true'
        # required for Qt bootstrap
        env['PREFERRED_ABI'] = arch.arch
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.Command(join(self.ctx.ndk_dir, "ndk-build")), "V=1", _env=env)


recipe = GenericNDKBuildRecipe()
