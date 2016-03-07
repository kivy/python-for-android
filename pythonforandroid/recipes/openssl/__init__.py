from functools import partial

from pythonforandroid.toolchain import Recipe, shprint, current_directory
import sh
from os.path import join


class OpenSSLRecipe(Recipe):
    version = '1.0.2g'
    url = 'https://www.openssl.org/source/openssl-{version}.tar.gz'

    def should_build(self, arch):
        return not self.has_libs(arch, 'libsslx.so', 'libcryptox.so')

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
            shprint(perl, 'Configure', 'shared', 'no-dso', 'no-krb5', buildarch, _env=env)

            self.apply_patch('disable-sover.patch', arch.arch)
            self.apply_patch('fix-shared-link.patch', arch.arch)

            check_crypto = partial(self.check_symbol, env, 'libcrypto.so')
            # check_ssl = partial(self.check_symbol, env, 'libssl.so')
            while True:
                shprint(sh.make, 'build_libs', _env=env)
                if all(map(check_crypto, ('SSLeay', 'MD5_Transform', 'MD4_Init'))):
                    break
                shprint(sh.make, 'clean', _env=env)

            # MUST BE RENAMED TO AVOID CONFLICTS WITH ANDROID'S DISTRIBUTED OPENSSL (IF INCLUDED INTO THE FINAL BUILD)
            libs_dir = self.get_build_dir(arch.arch)
            shprint(sh.cp, "-av", join(libs_dir, 'libcrypto.so'), join(libs_dir, 'libcryptox.so'))
            shprint(sh.cp, "-av", join(libs_dir, 'libssl.so'), join(libs_dir, 'libsslx.so'))
            self.install_libs(arch, 'libcryptox.so', 'libsslx.so')

recipe = OpenSSLRecipe()
