from pythonforandroid.toolchain import PythonRecipe, shprint, shutil, current_directory
from os.path import join, exists
import sh

class M2CryptoRecipe(PythonRecipe):
    version = '0.24.0'
    url = 'https://pypi.python.org/packages/source/M/M2Crypto/M2Crypto-{version}.tar.gz'
    #md5sum = '89557730e245294a6cab06de8ad4fb42'
    depends = ['openssl', 'hostpython2', 'python2', 'setuptools']
    site_packages_name = 'M2Crypto'
    call_hostpython_via_targetpython = False

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Fix missing build dir
            shprint(sh.mkdir, '-p', 'build/lib.' + 'linux-x86_64' + '-2.7/M2Crypto')
            # Build M2Crypto
            hostpython = sh.Command(self.hostpython_location)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    '-p' + arch.arch,
                    '-c' + 'unix',
                    '-o' + env['OPENSSL_BUILD_PATH'],
                    '-L' + env['OPENSSL_BUILD_PATH']
            , _env=env)
        # Install M2Crypto
        super(M2CryptoRecipe, self).build_arch(arch)

    def get_recipe_env(self, arch):
        env = super(M2CryptoRecipe, self).get_recipe_env(arch)
        env['OPENSSL_BUILD_PATH'] = self.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        env['CFLAGS'] += ' -I' + join(self.ctx.get_python_install_dir(), 'include/python2.7')
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -lpython2.7'
        return env

recipe = M2CryptoRecipe()
