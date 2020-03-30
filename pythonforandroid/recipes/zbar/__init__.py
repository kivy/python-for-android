from os.path import join
from pythonforandroid.recipe import PythonRecipe


class ZBarRecipe(PythonRecipe):

    version = '0.10'

    # For some reason the version 0.10 on PyPI is not the same as the ones
    # in sourceforge and GitHub. The one in PyPI has a setup.py.
    # url = 'https://github.com/ZBar/ZBar/archive/{version}.zip'
    url = 'https://pypi.python.org/packages/e0/5c/' + \
        'bd2a96a9f2adacffceb4482cdd56831735ab5a67ea6a60c0a8757c17b62e' + \
        '/zbar-{version}.tar.gz'

    call_hostpython_via_targetpython = False

    depends = ['setuptools', 'libzbar']

    patches = ["zbar-0.10-python-crash.patch"]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        libzbar = self.get_recipe('libzbar', self.ctx)
        libzbar_dir = libzbar.get_build_dir(arch.arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + join(libzbar_dir, 'include')
        env['LDFLAGS'] += ' -L' + join(libzbar_dir, 'zbar', '.libs')
        env['LIBS'] = env.get('LIBS', '') + ' -landroid -lzbar'
        return env


recipe = ZBarRecipe()
