
from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe, warning, Recipe

from os.path import join
import shutil

class MatplotlibRecipe(CppCompiledComponentsPythonRecipe):
    
    version = '3.0.3'
    url = 'https://github.com/matplotlib/matplotlib/archive/v{version}.zip'

    depends = ['numpy', 'setuptools', 'freetype', 'kiwisolver']

    python_depends = ['pyparsing', 'cycler', 'python-dateutil']

    # We need to patch to:
    # - make mpl build against the same numpy version as the numpy recipe
    #   (this could be done better by setting the target version dynamically)
    # - prevent mpl trying to build TkAgg, which wouldn't work on Android anyway but has build issues
    patches = ['mpl_android_fixes.patch']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(MatplotlibRecipe, self).get_recipe_env(arch)

        numpy_recipe = Recipe.get_recipe('numpy', self.ctx)
        
        env['NUMPY_INCLUDE_DIR'] = join(
            numpy_recipe.get_build_container_dir(arch.arch),
            'numpy', 'core', 'include')

        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/png -I{jni_path}/freetype/include'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))

        freetype_so_dir = join(
            Recipe.get_recipe('freetype', self.ctx).get_build_dir(arch),
            'objs', '.libs'
        )
        env['CFLAGS'] += ' -L{}'.format(freetype_so_dir)
        env['LDFLAGS'] += ' -L{}'.format(freetype_so_dir)

        env['CFLAGS'] += ' -L/home/sandy/kivytest'
        env['LDFLAGS'] += ' -L/home/sandy/kivytest'

        return env

    def prebuild_arch(self, arch):
        with open(join(self.get_recipe_dir(), 'setup.cfg.template')) as fileh:
            setup_cfg = fileh.read()

        with open(join(self.get_build_dir(arch), 'setup.cfg'), 'w') as fileh:
            fileh.write(setup_cfg.format(
                ndk_sysroot_usr=join(self.ctx.ndk_dir, 'sysroot', 'usr')))


recipe = MatplotlibRecipe()
