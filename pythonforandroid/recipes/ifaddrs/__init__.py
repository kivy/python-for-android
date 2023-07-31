""" ifaddrs for Android
"""
from os.path import join

import sh

from pythonforandroid.logger import shprint
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory
from pythonforandroid.util import ensure_dir


class IFAddrRecipe(CompiledComponentsPythonRecipe):
    version = '8f9a87c'
    url = 'https://github.com/morristech/android-ifaddrs/archive/{version}.zip'
    depends = ['hostpython3']

    call_hostpython_via_targetpython = False
    site_packages_name = 'ifaddrs'
    generated_libraries = ['libifaddrs.so']

    def prebuild_arch(self, arch):
        """Make the build and target directories"""
        path = self.get_build_dir(arch.arch)
        ensure_dir(path)

    def build_arch(self, arch):
        """simple shared compile"""
        env = self.get_recipe_env(arch, with_flags_in_cc=False)
        for path in (
                self.get_build_dir(arch.arch),
                join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Lib'),
                join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Include')):
            ensure_dir(path)
        cli = env['CC'].split()[0]
        # makes sure first CC command is the compiler rather than ccache, refs:
        # https://github.com/kivy/python-for-android/issues/1398
        if 'ccache' in cli:
            cli = env['CC'].split()[1]
        cc = sh.Command(cli)

        with current_directory(self.get_build_dir(arch.arch)):
            cflags = env['CFLAGS'].split()
            cflags.extend(['-I.', '-c', '-l.', 'ifaddrs.c', '-I.'])
            shprint(cc, *cflags, _env=env)
            cflags = env['CFLAGS'].split()
            cflags.extend(['-shared', '-I.', 'ifaddrs.o', '-o', 'libifaddrs.so'])
            cflags.extend(env['LDFLAGS'].split())
            shprint(cc, *cflags, _env=env)
            shprint(sh.cp, 'libifaddrs.so', self.ctx.get_libs_dir(arch.arch))


recipe = IFAddrRecipe()
