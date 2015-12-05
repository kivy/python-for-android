
from pythonforandroid.toolchain import Recipe, shprint, current_directory
from os.path import exists, join
import sh


class OpenSSLRecipe(Recipe):
    version = '1.0.2e'
    url = 'https://www.openssl.org/source/openssl-{version}.tar.gz'

    def should_build(self):
        return not exists(join(self.get_build_dir('armeabi'), 'libssl.a'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # sh fails with code 255 trying to execute ./Configure
            # so instead we manually run perl passing in Configure
            perl = sh.Command('perl')
            shprint(perl, 'Configure', 'no-dso', 'no-krb5', 'linux-armv4', _env=env)
            shprint(sh.make, 'build_libs', _env=env)

recipe = OpenSSLRecipe()
