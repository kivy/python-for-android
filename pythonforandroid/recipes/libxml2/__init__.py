from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh

class Libxml2Recipe(Recipe):
    version = '2.7.8'
    url = 'http://xmlsoft.org/sources/libxml2-{version}.tar.gz'
    depends = []

    def should_build(self, arch):
        super(Libxml2Recipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libxml2.a'))

    def build_arch(self, arch):
        super(Libxml2Recipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # If the build is done with /bin/sh things blow up,
            # try really hard to use bash
            bash = sh.Command('/bin/bash')
            sed = sh.Command('sed')
            make = sh.Command('make')
            shprint(bash, 'configure', '--build=i686-pc-linux-gnu', '--host=arm-linux-eabi',
                    '--without-modules',  '--without-legacy', '--without-history',  '--without-debug',  '--without-docbook', '--without-python', '--without-threads')
            shprint(make, _env=env)
            shutil.copyfile('.libs/libxml2.a', join(self.ctx.get_libs_dir(arch.arch), 'libxml2.a'))


    def get_recipe_env(self, arch):
        env = super(Libxml2Recipe, self).get_recipe_env(arch)
        env['CONFIG_SHELL'] = '/bin/bash'
        env['SHELL'] = '/bin/bash'
        return env

recipe = Libxml2Recipe()
