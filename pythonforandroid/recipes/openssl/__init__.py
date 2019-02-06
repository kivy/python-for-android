from os.path import join

from pythonforandroid.toolchain import Recipe, shprint, current_directory
import sh


class OpenSSLRecipe(Recipe):
    '''
    The OpenSSL libraries for python-for-android. This recipe will generate the
    following libraries as shared libraries (*.so):

        - crypto
        - ssl

    The generated openssl libraries are versioned, where the version is the
    recipe attribute :attr:`version` e.g.: ``libcrypto1.1.so``,
    ``libssl1.1.so``...so...to link your recipe with the openssl libs,
    remember to add the version at the end, e.g.:
    ``-lcrypto1.1 -lssl1.1``. Or better, you could do it dynamically
    using the methods: :meth:`include_flags`, :meth:`link_dirs_flags` and
    :meth:`link_libs_flags`.

    .. note:: the python2legacy version is too old to support openssl 1.1+, so
        we must use version 1.0.x. Also python3crystax is not building
        successfully with openssl libs 1.1+ so we use the legacy version as
        we do with python2legacy.

    .. warning:: This recipe is very sensitive because is used for our core
        recipes, the python recipes. The used API should match with the one
        used in our python build, otherwise we will be unable to build the
        _ssl.so python module.

    .. versionchanged:: 0.6.0

        - The gcc compiler has been deprecated in favour of clang and libraries
          updated to version 1.1.1 (LTS - supported until 11th September 2023)
        - Added two new methods to make easier to link with openssl:
          :meth:`include_flags` and :meth:`link_flags`
        - subclassed versioned_url
        - Adapted method :meth:`select_build_arch` to API 21+
        - Add ability to build a legacy version of the openssl libs when using
          python2legacy or python3crystax.

    '''

    standard_version = '1.1'
    '''the major minor version used to link our recipes'''
    legacy_version = '1.0'
    '''the major minor version used to link our recipes when using
    python2legacy or python3crystax'''

    standard_url_version = '1.1.1'
    '''the version used to download our libraries'''
    legacy_url_version = '1.0.2q'
    '''the version used to download our libraries when using python2legacy or
    python3crystax'''

    url = 'https://www.openssl.org/source/openssl-{url_version}.tar.gz'

    @property
    def use_legacy(self):
        if not self.ctx.recipe_build_order:
            return False
        return any([i for i in ('python2legacy', 'python3crystax') if
                    i in self.ctx.recipe_build_order])

    @property
    def version(self):
        if self.use_legacy:
            return self.legacy_version
        return self.standard_version

    @property
    def url_version(self):
        if self.use_legacy:
            return self.legacy_url_version
        return self.standard_url_version

    @property
    def versioned_url(self):
        if self.url is None:
            return None
        return self.url.format(url_version=self.url_version)

    def get_build_dir(self, arch):
        return join(self.get_build_container_dir(arch), self.name + self.version)

    def include_flags(self, arch):
        '''Returns a string with the include folders'''
        openssl_includes = join(self.get_build_dir(arch.arch), 'include')
        return (' -I' + openssl_includes +
                ' -I' + join(openssl_includes, 'internal') +
                ' -I' + join(openssl_includes, 'openssl'))

    def link_dirs_flags(self, arch):
        '''Returns a string with the appropriate `-L<lib directory>` to link
        with the openssl libs. This string is usually added to the environment
        variable `LDFLAGS`'''
        return ' -L' + self.get_build_dir(arch.arch)

    def link_libs_flags(self):
        '''Returns a string with the appropriate `-l<lib>` flags to link with
        the openssl libs. This string is usually added to the environment
        variable `LIBS`'''
        return ' -lcrypto{version} -lssl{version}'.format(version=self.version)

    def link_flags(self, arch):
        '''Returns a string with the flags to link with the openssl libraries
        in the format: `-L<lib directory> -l<lib>`'''
        return self.link_dirs_flags(arch) + self.link_libs_flags()

    def should_build(self, arch):
        return not self.has_libs(arch, 'libssl' + self.version + '.so',
                                 'libcrypto' + self.version + '.so')

    def get_recipe_env(self, arch=None):
        env = super(OpenSSLRecipe, self).get_recipe_env(arch, clang=not self.use_legacy)
        env['OPENSSL_VERSION'] = self.version
        env['MAKE'] = 'make'  # This removes the '-j5', which isn't safe
        if self.use_legacy:
            env['CFLAGS'] += ' ' + env['LDFLAGS']
            env['CC'] += ' ' + env['LDFLAGS']
        else:
            env['ANDROID_NDK'] = self.ctx.ndk_dir
        return env

    def select_build_arch(self, arch):
        aname = arch.arch
        if 'arm64' in aname:
            return 'android-arm64' if not self.use_legacy else 'linux-aarch64'
        if 'v7a' in aname:
            return 'android-arm' if not self.use_legacy else 'android-armv7'
        if 'arm' in aname:
            return 'android'
        if 'x86_64' in aname:
            return 'android-x86_64'
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
            config_args = ['shared', 'no-dso', 'no-asm']
            if self.use_legacy:
                config_args.append('no-krb5')
            config_args.append(buildarch)
            if not self.use_legacy:
                config_args.append('-D__ANDROID_API__={}'.format(self.ctx.ndk_api))
            shprint(perl, 'Configure', *config_args, _env=env)
            self.apply_patch(
                'disable-sover{}.patch'.format(
                    '-legacy' if self.use_legacy else ''), arch.arch)
            if self.use_legacy:
                self.apply_patch('rename-shared-lib.patch', arch.arch)

            shprint(sh.make, 'build_libs', _env=env)

            self.install_libs(arch, 'libssl' + self.version + '.so',
                              'libcrypto' + self.version + '.so')


recipe = OpenSSLRecipe()
