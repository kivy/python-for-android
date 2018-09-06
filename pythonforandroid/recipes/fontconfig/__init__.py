from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class FontconfigRecipe(BootstrapNDKRecipe):
    version = "really_old"
    url = 'https://github.com/vault/fontconfig/archive/androidbuild.zip'
    depends = ['sdl2']
    dir_name = 'fontconfig'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", 'fontconfig', _env=env)


recipe = FontconfigRecipe()
