from os.path import dirname, join, normpath
from sh import Command
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint


class Host_pip_recipe(PythonRecipe):
    name = 'pip'
    url = 'https://bootstrap.pypa.io/get-pip.py'

    depends = ['hostpython2']

    def unpack(self, arch):
        return

    def build_arch(self, arch):
        env = self.get_hostrecipe_env(arch)
        real_hostpython = Command(self.real_hostpython_location)
        script = join(self.ctx.packages_path, 'pip', 'get-pip.py')
        build_dir = normpath(join(dirname(self.real_hostpython_location),
                                  '..', self.name))
        target_dir = env['PYTHONPATH']
        ensure_dir(build_dir)
        with current_directory(build_dir):
            shprint(real_hostpython, script,
                    "--build={}".format(build_dir),
                    "--target={}".format(target_dir),
                    _env=env)


recipe = Host_pip_recipe()
