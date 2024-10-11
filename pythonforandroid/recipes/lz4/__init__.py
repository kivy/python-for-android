from os.path import join

from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class Lz4Recipe(CompiledComponentsPythonRecipe):
    name = 'lz4'
    version = '4.3.2'  # Use the desired version
    url = 'https://pypi.python.org/packages/source/l/lz4/lz4-{version}.tar.gz'
    depends = ['setuptools', 'liblz4']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        ctx = self.ctx

        # Include the headers from liblz4
        lz4_include_dir = join(ctx.get_python_install_dir(), 'include', 'lz4')
        env['CFLAGS'] += f' -I{lz4_include_dir}'

        # Link against the liblz4 library
        lz4_lib_dir = ctx.get_libs_dir(arch.arch)
        env['LDFLAGS'] += f' -L{lz4_lib_dir} -llz4'

        return env


recipe = Lz4Recipe()
