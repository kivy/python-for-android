from pythonforandroid.recipe import PythonRecipe
import shutil


class Kivy3Recipe(PythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/kivy3/archive/{version}.zip'

    depends = ['kivy']
    site_packages_name = 'kivy3'

    '''Due to setuptools.'''
    call_hostpython_via_targetpython = False

    def build_arch(self, arch):
        super().build_arch(arch)
        suffix = '/kivy3/default.glsl'
        shutil.copyfile(self.get_build_dir(arch.arch) + suffix, self.ctx.get_python_install_dir(arch.arch) + suffix)


recipe = Kivy3Recipe()
