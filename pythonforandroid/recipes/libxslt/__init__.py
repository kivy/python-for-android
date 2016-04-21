from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join, dirname, basename
import sh

class LibxsltRecipe(Recipe):
    version = '1.1.28'
    url = 'http://xmlsoft.org/sources/libxslt-{version}.tar.gz'
    depends = ['libxml2']
    patches = ['fix-dlopen.patch']

    call_hostpython_via_targetpython = False

    def should_build(self, arch):
        super(LibxsltRecipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libxslt.a'))

    def build_arch(self, arch):
        super(LibxsltRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # If the build is done with /bin/sh things blow up,
            # try really hard to use bash
            libxml = dirname(dirname(self.get_build_container_dir(arch.arch))) + "/libxml2/%s/libxml2" % arch.arch
            shprint(sh.Command('./configure'),
                    '--build=i686-pc-linux-gnu', '--host=arm-linux-eabi',
                    '--without-plugins', '--without-debug', '--without-python', '--without-crypto',
                    '--with-libxml-src=%s' % libxml)
            shprint(sh.make, _env=env)
            shutil.copyfile('libxslt/.libs/libxslt.a', join(self.ctx.get_libs_dir(arch.arch), 'libxslt.a'))


    def get_recipe_env(self, arch):
        env = super(LibxsltRecipe, self).get_recipe_env(arch)
        env['CONFIG_SHELL'] = '/bin/bash'
        env['SHELL'] = '/bin/bash'
        return env

recipe = LibxsltRecipe()
