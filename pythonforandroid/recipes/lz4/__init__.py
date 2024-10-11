from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join


class Lz4Recipe(CompiledComponentsPythonRecipe):
    name = 'lz4'
    version = '4.3.3'
    url = 'https://pypi.python.org/packages/source/l/lz4/lz4-{version}.tar.gz'
    depends = ['setuptools', 'liblz4']
    site_packages_name = 'lz4'

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        liblz4_recipe = self.get_recipe('liblz4', self.ctx)

        # Include the headers from liblz4
        lz4_includes = join(liblz4_recipe.get_build_dir(arch.arch), 'lib')
        env['CFLAGS'] += f' -I{lz4_includes}'

        # Link against the liblz4 library
        lz4_libs = join(liblz4_recipe.get_build_dir(arch.arch), 'lib')
        env['LDFLAGS'] += f' -L{lz4_libs} -llz4'

        return env


recipe = Lz4Recipe()
