from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import exists, join
import sh


class LibxsltRecipe(Recipe):
    version = '1.1.34'
    url = 'http://xmlsoft.org/sources/libxslt-{version}.tar.gz'
    depends = ['libxml2']
    patches = ['fix-dlopen.patch']
    built_libraries = {
        'libxslt.a': 'libxslt/.libs',
        'libexslt.a': 'libexslt/.libs'
    }

    call_hostpython_via_targetpython = False

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
            # If the build is done with /bin/sh things blow up,
            # try really hard to use bash
            libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)
            libxml2_build_dir = libxml2_recipe.get_build_dir(arch.arch)
            build_arch = shprint(sh.gcc, '-dumpmachine').stdout.decode(
                'utf-8').split('\n')[0]

            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            shprint(sh.Command('./configure'),
                    '--build=' + build_arch,
                    '--host=' + arch.command_prefix,
                    '--target=' + arch.command_prefix,
                    '--without-plugins',
                    '--without-debug',
                    '--without-python',
                    '--without-crypto',
                    '--with-libxml-src=' + libxml2_build_dir,
                    '--disable-shared',
                    _env=env)
            shprint(sh.make, "V=1", _env=env)

            shprint(sh.Command('chmod'), '+x', 'xslt-config')

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['CONFIG_SHELL'] = '/bin/bash'
        env['SHELL'] = '/bin/bash'

        libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)
        libxml2_build_dir = libxml2_recipe.get_build_dir(arch.arch)
        libxml2_libs_dir = join(libxml2_build_dir, '.libs')

        env['CFLAGS'] = ' '.join([
            env['CFLAGS'],
            '-I' + libxml2_build_dir,
            '-I' + join(libxml2_build_dir, 'include', 'libxml'),
            '-I' + self.get_build_dir(arch.arch),
        ])
        env['LDFLAGS'] += ' -L' + libxml2_libs_dir
        env['LIBS'] = '-lxml2 -lz -lm'

        return env


recipe = LibxsltRecipe()
