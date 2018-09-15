from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import (is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from os.path import exists, join, realpath
import sh


class Python3Recipe(TargetPythonRecipe):
    version = "3.7"
    url = 'https://github.com/inclement/cpython/archive/bpo-30386.zip'
    name = 'python3'

    depends = []
    conflicts = ['python3crystax', 'python2']
    # opt_depends = ['openssl', 'sqlite3']

    from_crystax = False

    def build_arch(self, arch):

        # If already built, don't build again
        if not exists(join(self.get_build_dir(arch.arch), 'Android', 'build', 'python3.7-android-{}-armv7'.format(self.ctx.ndk_target_api), 'libpython3.7m.so')):
            self.do_python_build(arch)

        # if not exists(self.ctx.get_python_install_dir()):
        #     shprint(sh.cp, '-a', join(self.get_build_dir(arch.arch), 'python-install'),
        #             self.ctx.get_python_install_dir())

        # # This should be safe to run every time
        # info('Copying hostpython binary to targetpython folder')
        # shprint(sh.cp, self.ctx.hostpython,
        #         join(self.ctx.get_python_install_dir(), 'bin', 'python.host'))
        # self.ctx.hostpython = join(self.ctx.get_python_install_dir(), 'bin', 'python.host')

        # if not exists(join(self.ctx.get_libs_dir(arch.arch), 'libpython2.7.so')):
        #     shprint(sh.cp, join(self.get_build_dir(arch.arch), 'libpython2.7.so'), self.ctx.get_libs_dir(arch.arch))
        # Instead of using a locally built hostpython, we use the
        # user's Python for now. They must have the right version
        # available. Using e.g. pyenv makes this easy.
        self.ctx.hostpython = 'python{}'.format(self.version)

        recipe_dir = self.get_build_dir(arch.arch)
        shprint(sh.cp,
                join(recipe_dir, 'Android', 'build',
                     'python3.7-android-{}-armv7'.format(self.ctx.ndk_target_api),
                     'pyconfig.h'),
                join(recipe_dir, 'Include'))
                


    def do_python_build(self, arch):

        import os
        env = os.environ

        env.update({'ANDROID_NDK_ROOT': self.ctx.ndk_dir,
                    'ANDROID_API': str(self.ctx.ndk_target_api),
                    'ANDROID_ARCH': 'armv7'})

        with current_directory(join(self.get_build_dir(arch.arch), 'Android')):
            com = sh.Command('./makesetup')
            # import ipdb
            # ipdb.set_trace()
            shprint(com, _env=env)

            shprint(sh.make, 'build', _env=env)
        


recipe = Python3Recipe()
