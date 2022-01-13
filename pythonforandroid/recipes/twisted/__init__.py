import os
import shutil

from pythonforandroid.recipe import CythonRecipe


class TwistedRecipe(CythonRecipe):
    version = '20.3.0'
    url = 'https://github.com/twisted/twisted/archive/twisted-{version}.tar.gz'

    depends = ['setuptools', 'zope_interface', 'incremental', 'constantly']
    patches = ['incremental.patch', 'remove_tests.patch']

    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        # TODO Need to whitelist tty.pyo and termios.so here

        # remove the unit test dirs
        source_dir = os.path.join(self.get_build_dir(arch.arch), 'src/twisted')
        for item in os.walk(source_dir):
            if os.path.basename(item[0]) == 'test':
                full_path = os.path.join(source_dir, item[0])
                shutil.rmtree(full_path, ignore_errors=True)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # We add BUILDLIB_PATH to PYTHONPATH so twisted can find _io.so
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(arch),
            env['BUILDLIB_PATH'],
        ])
        return env


recipe = TwistedRecipe()
