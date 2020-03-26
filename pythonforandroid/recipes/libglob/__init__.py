"""
    android libglob
    available via '-lglob' LDFLAG
"""
from os.path import exists, join
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory
from pythonforandroid.logger import info, shprint
import sh


class LibGlobRecipe(Recipe):
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
    built_libraries = {'libglob.so': '.'}

    depends = ['hostpython3']
    patches = ['glob.patch']

    def should_build(self, arch):
        """It's faster to build than check"""
        return True

    def prebuild_arch(self, arch):
        """Make the build and target directories"""
        path = self.get_build_dir(arch.arch)
        if not exists(path):
            info("creating {}".format(path))
            shprint(sh.mkdir, '-p', path)

    def build_arch(self, arch):
        """simple shared compile"""
        env = self.get_recipe_env(arch, with_flags_in_cc=False)
        for path in (
                self.get_build_dir(arch.arch),
                join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Lib'),
                join(self.ctx.python_recipe.get_build_dir(arch.arch), 'Include')):
            if not exists(path):
                info("creating {}".format(path))
                shprint(sh.mkdir, '-p', path)
        cli = env['CC'].split()[0]
        # makes sure first CC command is the compiler rather than ccache, refs:
        # https://github.com/kivy/python-for-android/issues/1399
        if 'ccache' in cli:
            cli = env['CC'].split()[1]
        cc = sh.Command(cli)

        with current_directory(self.get_build_dir(arch.arch)):
            cflags = env['CFLAGS'].split()
            cflags.extend(['-I.', '-c', '-l.', 'glob.c', '-I.'])
            shprint(cc, *cflags, _env=env)
            cflags = env['CFLAGS'].split()
            cflags.extend(['-shared', '-I.', 'glob.o', '-o', 'libglob.so'])
            cflags.extend(env['LDFLAGS'].split())
            shprint(cc, *cflags, _env=env)


recipe = LibGlobRecipe()
