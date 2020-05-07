from pythonforandroid.recipe import CythonRecipe
from os.path import join


class ShapelyRecipe(CythonRecipe):
    version = '1.7a1'
    url = 'https://github.com/Toblerity/Shapely/archive/{version}.tar.gz'
    depends = ['setuptools', 'libgeos']

    call_hostpython_via_targetpython = False

    # Patch to avoid libgeos check (because it fails), insert environment
    # variables for our libgeos build (includes, lib paths...) and force
    # the cython's compilation to raise an error in case that it fails
    patches = ['setup.patch']

    # Don't Force Cython
    # setup_extra_args = ['sdist']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch)

        libgeos_install = join(self.get_recipe(
            'libgeos', self.ctx).get_build_dir(arch.arch), 'install_target')
        # All this `GEOS_X` variables should be string types, separated
        # by commas in case that we need to pass more than one value
        env['GEOS_INCLUDE_DIRS'] = join(libgeos_install, 'include')
        env['GEOS_LIBRARY_DIRS'] = join(libgeos_install, 'lib')
        env['GEOS_LIBRARIES'] = 'geos_c,geos'

        return env


recipe = ShapelyRecipe()
