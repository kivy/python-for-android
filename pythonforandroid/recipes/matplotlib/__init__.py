
from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe

from os.path import join


class MatplotlibRecipe(CppCompiledComponentsPythonRecipe):

    version = '3.0.3'
    url = 'https://github.com/matplotlib/matplotlib/archive/v{version}.zip'

    depends = ['numpy', 'png', 'setuptools', 'freetype', 'kiwisolver']

    python_depends = ['pyparsing', 'cycler', 'python-dateutil']

    # We need to patch to:
    # - make mpl build against the same numpy version as the numpy recipe
    #   (this could be done better by setting the target version dynamically)
    # - prevent mpl trying to build TkAgg, which wouldn't work on Android anyway but has build issues
    patches = ['mpl_android_fixes.patch']

    call_hostpython_via_targetpython = False

    def prebuild_arch(self, arch):
        with open(join(self.get_recipe_dir(), 'setup.cfg.template')) as fileh:
            setup_cfg = fileh.read()

        with open(join(self.get_build_dir(arch), 'setup.cfg'), 'w') as fileh:
            fileh.write(setup_cfg.format(
                ndk_sysroot_usr=join(self.ctx.ndk_dir, 'sysroot', 'usr')))


recipe = MatplotlibRecipe()
