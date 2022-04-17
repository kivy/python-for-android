from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import exists
import sh


class Libxml2Recipe(Recipe):
    version = '2.9.12'
    url = 'http://xmlsoft.org/sources/libxml2-{version}.tar.gz'
    depends = []
    patches = ['add-glob.c.patch']
    built_libraries = {'libxml2.a': '.libs'}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):

            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            build_arch = shprint(
                sh.gcc, '-dumpmachine').stdout.decode('utf-8').split('\n')[0]
            shprint(sh.Command('./configure'),
                    '--build=' + build_arch,
                    '--host=' + arch.command_prefix,
                    '--target=' + arch.command_prefix,
                    '--without-modules',
                    '--without-legacy',
                    '--without-history',
                    '--without-debug',
                    '--without-docbook',
                    '--without-python',
                    '--without-threads',
                    '--without-iconv',
                    '--without-lzma',
                    '--disable-shared',
                    '--enable-static',
                    _env=env)

            # Ensure we only build libxml2.la as if we do everything
            # we'll need the glob dependency which is a big headache
            shprint(sh.make, "libxml2.la", _env=env)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['CONFIG_SHELL'] = '/bin/bash'
        env['SHELL'] = '/bin/bash'
        env['CC'] += ' -I' + self.get_build_dir(arch.arch)
        return env


recipe = Libxml2Recipe()
