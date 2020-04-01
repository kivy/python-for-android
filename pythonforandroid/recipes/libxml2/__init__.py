from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint, shutil, current_directory
from os.path import exists, join
import sh


class Libxml2Recipe(Recipe):
    version = '2.9.8'
    url = 'http://xmlsoft.org/sources/libxml2-{version}.tar.gz'
    depends = []
    patches = ['add-glob.c.patch']

    def should_build(self, arch):
        super(Libxml2Recipe, self).should_build(arch)
        return not exists(
            join(self.get_build_dir(arch.arch), '.libs', 'libxml2.a'))

    def build_arch(self, arch):
        super(Libxml2Recipe, self).build_arch(arch)
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

            shutil.copyfile('.libs/libxml2.a',
                            join(self.ctx.libs_dir, 'libxml2.a'))

    def get_recipe_env(self, arch):
        env = super(Libxml2Recipe, self).get_recipe_env(arch)
        env['CONFIG_SHELL'] = '/bin/bash'
        env['SHELL'] = '/bin/bash'
        env['CC'] += ' -I' + self.get_build_dir(arch.arch)
        return env


recipe = Libxml2Recipe()
