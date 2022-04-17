from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import will_build
import sh
from os.path import join


class PyjniusRecipe(CythonRecipe):
    version = '1.4.2'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = [('genericndkbuild', 'sdl2'), 'six']
    site_packages_name = 'jnius'

    patches = [('genericndkbuild_jnienv_getter.patch', will_build('genericndkbuild'))]

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        return env

    def postbuild_arch(self, arch):
        super().postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
