from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class ApswRecipe(PythonRecipe):
    version = '3.15.0-r1'
    url = 'https://github.com/rogerbinns/apsw/archive/{version}.tar.gz'
    depends = ['sqlite3', 'setuptools']
    call_hostpython_via_targetpython = False
    site_packages_name = 'apsw'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Build python bindings
            hostpython = sh.Command(self.hostpython_location)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    '--enable=fts4', _env=env)
        # Install python bindings
        super().build_arch(arch)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        sqlite_recipe = self.get_recipe('sqlite3', self.ctx)
        env['CFLAGS'] += ' -I' + sqlite_recipe.get_build_dir(arch.arch)
        env['LDFLAGS'] += ' -L' + sqlite_recipe.get_lib_dir(arch)
        env['LIBS'] = env.get('LIBS', '') + ' -lsqlite3'
        return env


recipe = ApswRecipe()
