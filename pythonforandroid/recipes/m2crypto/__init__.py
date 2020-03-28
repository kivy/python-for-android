from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory
from pythonforandroid.logger import shprint, info
import glob
import sh


class M2CryptoRecipe(CompiledComponentsPythonRecipe):
    version = '0.30.1'
    url = 'https://pypi.python.org/packages/source/M/M2Crypto/M2Crypto-{version}.tar.gz'
    depends = ['openssl', 'setuptools']
    site_packages_name = 'M2Crypto'
    call_hostpython_via_targetpython = False

    def build_compiled_components(self, arch):
        info('Building compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Build M2Crypto
            hostpython = sh.Command(self.hostpython_location)
            if self.install_in_hostpython:
                shprint(hostpython, 'setup.py', 'clean', '--all', _env=env)
            shprint(hostpython, 'setup.py', self.build_cmd,
                    '-p' + arch.arch,
                    '-c' + 'unix',
                    '-o' + env['OPENSSL_BUILD_PATH'],
                    '-L' + env['OPENSSL_BUILD_PATH'],
                    _env=env, *self.setup_extra_args)
            build_dir = glob.glob('build/lib.*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['OPENSSL_BUILD_PATH'] = self.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        return env


recipe = M2CryptoRecipe()
