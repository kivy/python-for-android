from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh

class LibxsltRecipe(Recipe):
    version = '1.1.28'
    url = 'http://xmlsoft.org/sources/libxslt-{version}.tar.gz'
    depends = ['libxml2']
    patches = ['fix-dlopen.patch']

    def should_build(self, arch):
        super(LibxsltRecipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libxslt.a'))

    def build_arch(self, arch):
        super(LibxsltRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            bash = sh.Command('bash')
            shprint(bash, 'configure',
                    '--build=i686-pc-linux-gnu', '--host=arm-linux-eabi',
                    '--without-plugins', '--without-debug', '--without-python', '--without-crypto',
                    '--with-libxml-src=$BUILD_libxml2')
            shprint(sh.make, _env=env)
            shutil.copyfile('src/libxslt/.libs/libxslt.a', join(self.ctx.get_libs_dir(arch.arch), 'libxslt.a'))


    def get_recipe_env(self, arch):
        env = super(LibXml2Recipe, self).get_recipe_env(arch)
        env['CFLAGS'] += ' -Os'
        return env

recipe = LibxsltRecipe()
