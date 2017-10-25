""" ifaddrs for Android
"""
from os.path import join, exists
import sh
from pythonforandroid.logger import info, shprint

from pythonforandroid.toolchain import (CompiledComponentsPythonRecipe,
                                        current_directory)

class IFAddrRecipe(CompiledComponentsPythonRecipe):
    version = 'master'
    url = 'git+https://github.com/morristech/android-ifaddrs.git'
    depends = [('hostpython2', 'hostpython3'), ('python2', 'python3crystax')]

    call_hostpython_via_targetpython = False
    site_packages_name = 'ifaddrs'
    generated_libraries = ['libifaddrs.so']

    def should_build(self, arch):
        """It's faster to build than check"""
        return not (exists(join(self.ctx.libs_dir, arch.arch, 'libifaddrs.so'))
                    and exists(join(self.ctx.get_python_install_dir(), 'lib'
                        "libifaddrs.so"))
                    )

    def prebuild_arch(self, arch):
        """Make the build and target directories"""
        path = self.get_build_dir(arch.arch)
        if not  exists(path):
            info("creating {}".format(path))
            shprint(sh.mkdir, '-p', path)

    def build_arch(self, arch):
        """simple shared compile"""
        env = self.get_recipe_env(arch, with_flags_in_cc=False)
        for path in (self.get_build_dir(arch.arch),
            join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Lib'),
            join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Include'),
                    ):
            if not  exists(path):
                info("creating {}".format(path))
                shprint(sh.mkdir, '-p', path)
        cli = env['CC'].split()
        cc = sh.Command(cli[0])

        with current_directory(self.get_build_dir(arch.arch)):
            cflags = env['CFLAGS'].split()
            cflags.extend(['-I.', '-c', '-l.', 'ifaddrs.c', '-I.'])
            shprint(cc, *cflags, _env=env)

            cflags = env['CFLAGS'].split()
            cflags.extend(['-shared', '-I.', 'ifaddrs.o', '-o', 'libifaddrs.so'])
            cflags.extend(env['LDFLAGS'].split())
            shprint(cc, *cflags, _env=env)

            shprint(sh.cp, 'libifaddrs.so', self.ctx.get_libs_dir(arch.arch))
            shprint(sh.cp, "libifaddrs.so", join(self.ctx.get_python_install_dir(), 'lib'))
            # drop header in to the Python include directory
            shprint(sh.cp, "ifaddrs.h", join(self.ctx.get_python_install_dir(),
                                          'include/python{}'.format(
                                              self.ctx.python_recipe.version[0:3]
                                          )
                                         )
                   )
            include_path = join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Include')
            shprint(sh.cp, "ifaddrs.h", include_path)

recipe = IFAddrRecipe()
