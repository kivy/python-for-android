from functools import partial
from pythonforandroid.toolchain import Recipe, current_directory
from pythonforandroid.logger import shprint
from os.path import join, exists
import sh

class OpenSSLRecipe(Recipe):
    version = '1.0.2g'
    url = 'https://www.openssl.org/source/openssl-{version}.tar.gz'

    def should_build(self, arch):
        if exists(join(self.get_build_dir(arch.arch), 'libssl.a')):
            return False
        return True

    def check_symbol(self, env, sofile, symbol):
        nm = env.get('NM', 'nm')
        syms = sh.sh('-c', "{} -gp {} | cut -d' ' -f3".format(
                nm, sofile), _env=env).splitlines()
        if symbol in syms:
            return True
        print('{} missing symbol {}; rebuilding'.format(sofile, symbol))
        return False

    def get_recipe_env(self, arch=None):
        env = super(OpenSSLRecipe, self).get_recipe_env(arch)
        env['CFLAGS'] += ' ' + env['LDFLAGS']
        env['CC'] += ' ' + env['LDFLAGS']
        return env

    def select_build_arch(self, arch):
        aname = arch.arch
        if 'arm64' in aname:
            return 'linux-aarch64'
        if 'v7a' in aname:
            return 'android-armv7'
        if 'arm' in aname:
            return 'android'
        return 'linux-armv4'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # sh fails with code 255 trying to execute ./Configure
            # so instead we manually run perl passing in Configure
            perl = sh.Command('perl')
            buildarch = self.select_build_arch(arch)

            # NOTE: Disabled the build of shared libraries to prevent anything to be
            # linked against them by mistake. It's better to build the openssl libs as
            # static because this way we avoid conflicts with the openssl libs
            # distributed with android system. You can enable the build of shared libs
            # adding the keyword 'shared' into the below configure command, but probably,
            # your app will not be able to use the compiled openssl libraries because
            # when the app loads them, first will use the system ones,instead of the compiled
            shprint(perl, 'Configure', 'no-dso', 'no-krb5', buildarch, _env=env)

            self.apply_patch('disable-sover.patch', arch.arch)

            check_crypto = partial(self.check_symbol, env, 'libcrypto.a')
            # check_ssl = partial(self.check_symbol, env, 'libssl.a')
            while True:
                shprint(sh.make, 'build_libs', _env=env)
                if all(map(check_crypto, ('SSLeay', 'MD5_Transform', 'MD4_Init'))):
                    break
                shprint(sh.make, 'clean', _env=env)

            if exists('libssl.so'):
                self.install_libs(arch, 'libssl.so', 'libcrypto.so')
            else:
                shprint(sh.cp, 'libssl.a', self.ctx.libs_dir)
                shprint(sh.cp, 'libcrypto.a', self.ctx.libs_dir)

recipe = OpenSSLRecipe()
