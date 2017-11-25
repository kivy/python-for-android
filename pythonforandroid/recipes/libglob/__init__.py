"""
    android libglob
    available via '-lglob' LDFLAG
"""
from os.path import exists, join, dirname
from pythonforandroid.toolchain import (CompiledComponentsPythonRecipe,
                                        current_directory)
from pythonforandroid.logger import shprint, info, warning, info_main
import sh

class LibGlobRecipe(CompiledComponentsPythonRecipe):
    """Make a glob.h and glob.so for the python_install_dir()"""
    version = '0.0.1'
    url = None
    # 
    # glob.h and glob.c extracted from
    # https://github.com/white-gecko/TokyoCabinet, e.g.:
    #   https://raw.githubusercontent.com/white-gecko/TokyoCabinet/master/glob.h
    #   https://raw.githubusercontent.com/white-gecko/TokyoCabinet/master/glob.c
    # and pushed in via patch
    name = 'libglob'

    depends = [('hostpython2', 'hostpython3'), ('python2', 'python3crystax')]
    patches = ['glob.patch']

    def should_build(self, arch):
        """It's faster to build than check"""
        return True

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
            cflags.extend(['-I.', '-c', '-l.', 'glob.c', '-I.']) # , '-o', 'glob.o'])
            shprint(cc, *cflags, _env=env)

            cflags = env['CFLAGS'].split()
            srindex = cflags.index('--sysroot')
            if srindex:
                cflags[srindex+1] = self.ctx.ndk_platform
            cflags.extend(['-shared', '-I.', 'glob.o', '-o', 'libglob.so'])
            shprint(cc, *cflags, _env=env)

            shprint(sh.cp, 'libglob.so', join(self.ctx.libs_dir, arch.arch))
            shprint(sh.cp, "libglob.so", join(self.ctx.get_python_install_dir(), 'lib'))
            # drop header in to the Python include directory
            shprint(sh.cp, "glob.h", join(self.ctx.get_python_install_dir(),
                                          'include/python{}'.format(
                                              self.ctx.python_recipe.version[0:3]
                                          )
                                         )
                   )
            include_path = join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Include')
            shprint(sh.cp, "glob.h", include_path)

recipe = LibGlobRecipe()
