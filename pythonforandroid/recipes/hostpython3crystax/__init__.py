
from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
from os.path import join, exists
from os import chdir
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()


class Hostpython3Recipe(Recipe):
    version = '3.5'
    # url = 'http://python.org/ftp/python/{version}/Python-{version}.tgz'
    # url = 'https://github.com/crystax/android-vendor-python-3-5/archive/master.zip'
    name = 'hostpython3crystax'

    conflicts = ['hostpython2']

    # def prebuild_armeabi(self):
    #     # Override hostpython Setup?
    #     shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
    #             join(self.get_build_dir('armeabi'), 'Modules', 'Setup'))

    def build_arch(self, arch):
        self.ctx.hostpython = '/usr/bin/false'
        self.ctx.hostpgen = '/usr/bin/false'


recipe = Hostpython3Recipe()
