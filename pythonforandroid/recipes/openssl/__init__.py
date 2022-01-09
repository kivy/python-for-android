from os.path import join

from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
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

    .. versionchanged:: 2019.06.06.1.dev0

        - Removed legacy version of openssl libraries

    '''

    version = '1.1'
    '''the major minor version used to link our recipes'''

    url_version = '1.1.1m'
    '''the version used to download our libraries'''

    url = 'https://www.openssl.org/source/openssl-{url_version}.tar.gz'

    built_libraries = {
        'libcrypto{version}.so'.format(version=version): '.',
        'libssl{version}.so'.format(version=version): '.',
    }

    @property
    def versioned_url(self):
        if self.url is None:
            return None
        return self.url.format(url_version=self.url_version)

    def get_build_dir(self, arch):
        return join(
            self.get_build_container_dir(arch), self.name + self.version
        )

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

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['OPENSSL_VERSION'] = self.version
        env['MAKE'] = 'make'  # This removes the '-j5', which isn't safe
        env['CC'] = 'clang'
        env['ANDROID_NDK_HOME'] = self.ctx.ndk_dir
        return env

    def select_build_arch(self, arch):
        aname = arch.arch
        if 'arm64' in aname:
            return 'android-arm64'
        if 'v7a' in aname:
            return 'android-arm'
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
            config_args = [
                'shared',
                'no-dso',
                'no-asm',
                buildarch,
                '-D__ANDROID_API__={}'.format(self.ctx.ndk_api),
            ]
            shprint(perl, 'Configure', *config_args, _env=env)
            self.apply_patch('disable-sover.patch', arch.arch)

            shprint(sh.make, 'build_libs', _env=env)


recipe = OpenSSLRecipe()
