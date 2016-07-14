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
            # Build M2Crypto
            hostpython = sh.Command(self.hostpython_location)
            r = self.get_recipe('openssl', self.ctx)
            openssl_dir = r.get_build_dir(arch.arch)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    '-p' + arch.arch,
                    '-c' + 'unix',
                    '--openssl=' + openssl_dir
            , _env=env)
        # Install M2Crypto
        super(M2CryptoRecipe, self).build_arch(arch)

    def get_recipe_env(self, arch):
        env = super(M2CryptoRecipe, self).get_recipe_env(arch)
        r = self.get_recipe('openssl', self.ctx)
        openssl_dir = r.get_build_dir(arch.arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7' + \
                         ' -I' + join(openssl_dir, 'include')
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -L' + openssl_dir + \
                          ' -lpython2.7' + \
                          ' -lssl' + r.version + \
                          ' -lcrypto' + r.version
        return env

recipe = M2CryptoRecipe()
