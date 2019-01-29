from pythonforandroid.recipe import Recipe, CythonRecipe


class ShapelyRecipe(CythonRecipe):
    version = '1.5'
    url = 'https://github.com/Toblerity/Shapely/archive/master.zip'
    depends = ['setuptools', 'libgeos']
    call_hostpython_via_targetpython = False

    patches = ['setup.patch']  # Patch to force setup to fail when C extention fails to build

    # setup_extra_args = ['sdist'] # DontForce Cython

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        """ Add libgeos headers to path """
        env = super(ShapelyRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        libgeos_dir = Recipe.get_recipe('libgeos', self.ctx).get_build_dir(arch.arch)
        env['CFLAGS'] += " -I{}/dist/include".format(libgeos_dir)
        return env


recipe = ShapelyRecipe()
