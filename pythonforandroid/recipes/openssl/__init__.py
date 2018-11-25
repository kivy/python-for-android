from functools import partial

from pythonforandroid.toolchain import Recipe, shprint, current_directory
import sh


class OpenSSLRecipe(Recipe):
    version = '1.1.1'
    lib_version = '1.1'
    url = 'https://www.openssl.org/source/openssl-{version}.tar.gz'

    def should_build(self, arch):
        return not self.has_libs(arch, 'libssl' + self.lib_version + '.so',
                                 'libcrypto' + self.lib_version + '.so')

    def check_symbol(self, env, sofile, symbol):
        nm = env.get('NM', 'nm')
        syms = sh.sh('-c', "{} -gp {} | cut -d' ' -f3".format(
                nm, sofile), _env=env).splitlines()
        if symbol in syms:
            return True
        print('{} missing symbol {}; rebuilding'.format(sofile, symbol))
        return False

    def get_recipe_env(self, arch=None):
        env = super(OpenSSLRecipe, self).get_recipe_env(arch, clang=True)
        env['OPENSSL_VERSION'] = self.lib_version
        env['MAKE'] = 'make'  # This removes the '-j5', which isn't safe
        env['ANDROID_NDK'] = self.ctx.ndk_dir
        return env

    def select_build_arch(self, arch):
        aname = arch.arch
        if 'arm64' in aname:
            return 'linux-aarch64'
        if 'v7a' in aname:
            return 'android-arm'
        if 'arm' in aname:
            return 'android'
        if 'x86' in aname:
            return 'android-x86'
        return 'linux-armv4'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # sh fails with code 255 trying to execute ./Configure
            # so instead we manually run perl passing in Configure
            perl = sh.Command('perl')
            buildarch = self.select_build_arch(arch)
            # XXX if we don't have no-asm, using clang and ndk-15c, i got:
            # crypto/aes/bsaes-armv7.S:1372:14: error: immediate operand must be in the range [0,4095]
            #  add r8, r6, #.LREVM0SR-.LM0 @ borrow r8
            #              ^
            # crypto/aes/bsaes-armv7.S:1434:14: error: immediate operand must be in the range [0,4095]
            #  sub r6, r8, #.LREVM0SR-.LSR @ pass constants
            shprint(perl, 'Configure', 'shared', 'no-dso', 'no-asm', buildarch, _env=env)
            self.apply_patch('disable-sover.patch', arch.arch)

            # check_ssl = partial(self.check_symbol, env, 'libssl' + self.version + '.so')
            check_crypto = partial(self.check_symbol, env, 'libcrypto' + self.lib_version + '.so')
            while True:
                shprint(sh.make, 'build_libs', _env=env)
                if all(map(check_crypto, ('MD5_Transform', 'MD4_Init'))):
                    break
                import time
                time.sleep(3)
                shprint(sh.make, 'clean', _env=env)

            self.install_libs(arch, 'libssl' + self.lib_version + '.so',
                              'libcrypto' + self.lib_version + '.so')


recipe = OpenSSLRecipe()
