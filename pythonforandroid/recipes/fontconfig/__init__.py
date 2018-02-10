
from pythonforandroid.toolchain import BootstrapNDKRecipe, shprint, current_directory, info_main
from os.path import exists, join
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()


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
