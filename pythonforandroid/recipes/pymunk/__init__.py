from pythonforandroid.toolchain import PythonRecipe
from pythonforandroid.toolchain import CythonRecipe
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import info

import os.path

class PymunkRecipe(CompiledComponentsPythonRecipe):
    name = "pymunk"
    version = '5.2.0'
    url = 'https://pypi.python.org/packages/5e/bd/e67edcffdee3d0a1e3ebf0050bb9746a61d616f5502ceedddf0f7fd0a896/pymunk-5.2.0.zip'
    depends = [('python2', 'python3crystax'), 'cffi', 'setuptools']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(PymunkRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        arch_noeabi = arch.arch.replace('eabi', '')
        env['LDFLAGS'] += " -shared -llog"
        env['LDFLAGS'] += " -landroid -lpython2.7"
        env['LDFLAGS'] += " --sysroot={ctx.ndk_dir}/platforms/android-{ctx.android_api}/arch-{arch_noeabi}".format(
		ctx=self.ctx, arch_noeabi=arch_noeabi)
        return env

recipe = PymunkRecipe()
