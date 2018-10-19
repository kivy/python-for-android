from pythonforandroid.toolchain import (
    Bootstrap, shprint, current_directory, info, info_main)
from pythonforandroid.util import ensure_dir
from os.path import join, exists, curdir, abspath
from os import walk
import os
import glob
import sh


EXCLUDE_EXTS = (".py", ".pyc", ".so.o", ".so.a", ".so.libs", ".pyx")


class SDL2GradleBootstrap(Bootstrap):
    name = 'sdl2'

    recipe_depends = ['sdl2', ('python2', 'python3', 'python3crystax')]

    def run_distribute(self):
        info_main("# Creating Android project ({})".format(self.name))

        arch = self.ctx.archs[0]
        python_install_dir = self.ctx.get_python_install_dir()
        from_crystax = self.ctx.python_recipe.from_crystax
        crystax_python_dir = join("crystax_python", "crystax_python")

        python_bundle_dir = join('_python_bundle', '_python_bundle')

        if len(self.ctx.archs) > 1:
            raise ValueError("SDL2/gradle support only one arch")

        info("Copying SDL2/gradle build for {}".format(arch))
        shprint(sh.rm, "-rf", self.dist_dir)
        shprint(sh.cp, "-r", self.build_dir, self.dist_dir)

        # either the build use environment variable (ANDROID_HOME)
        # or the local.properties if exists
        with current_directory(self.dist_dir):
            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

        # TODO: Move the packaged python building to the python recipes
        with current_directory(self.dist_dir):
            info("Copying Python distribution")

            if 'python2' in self.ctx.recipe_build_order:
                ensure_dir("private")
            elif not exists("crystax_python") and from_crystax:
                ensure_dir(crystax_python_dir)
            elif 'python3' in self.ctx.recipe_build_order:
                ensure_dir(python_bundle_dir)

            hostpython = sh.Command(self.ctx.hostpython)
            if self.ctx.python_recipe.name == 'python2':
                try:
                    shprint(hostpython, '-OO', '-m', 'compileall',
                            python_install_dir,
                            _tail=10, _filterout="^Listing")
                except sh.ErrorReturnCode:
                    pass
                if 'python2' in self.ctx.recipe_build_order and not exists('python-install'):
                    shprint(
                        sh.cp, '-a', python_install_dir, './python-install')

            self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
            self.distribute_javaclasses(self.ctx.javaclass_dir,
                                        dest_dir=join("src", "main", "java"))

            if self.ctx.python_recipe.name == 'python2':
                info("Filling private directory")
                if not exists(join("private", "lib")):
                    info("private/lib does not exist, making")
                    shprint(sh.cp, "-a",
                            join("python-install", "lib"), "private")
                shprint(sh.mkdir, "-p",
                        join("private", "include", "python2.7"))

                libpymodules_fn = join("libs", arch.arch, "libpymodules.so")
                if exists(libpymodules_fn):
                    shprint(sh.mv, libpymodules_fn, 'private/')
                shprint(sh.cp,
                        join('python-install', 'include',
                             'python2.7', 'pyconfig.h'),
                        join('private', 'include', 'python2.7/'))

                info('Removing some unwanted files')
                shprint(sh.rm, '-f', join('private', 'lib', 'libpython2.7.so'))
                shprint(sh.rm, '-rf', join('private', 'lib', 'pkgconfig'))

                libdir = join(self.dist_dir, 'private', 'lib', 'python2.7')
                site_packages_dir = join(libdir, 'site-packages')
                with current_directory(libdir):
                    removes = []
                    for dirname, root, filenames in walk("."):
                        for filename in filenames:
                            for suffix in EXCLUDE_EXTS:
                                if filename.endswith(suffix):
                                    removes.append(filename)
                    shprint(sh.rm, '-f', *removes)

                    info('Deleting some other stuff not used on android')
                    # To quote the original distribute.sh, 'well...'
                    shprint(sh.rm, '-rf', 'lib2to3')
                    shprint(sh.rm, '-rf', 'idlelib')
                    for filename in glob.glob('config/libpython*.a'):
                        shprint(sh.rm, '-f', filename)
                    shprint(sh.rm, '-rf', 'config/python.o')

            elif self.ctx.python_recipe.name == 'python3':
                self.ctx.python_recipe.create_python_bundle(
                    join(self.dist_dir, python_bundle_dir), arch)
                
            elif self.ctx.python_recipe.from_crystax:
                self.ctx.python_recipe.create_python_bundle(
                    join(self.dist_dir, python_bundle_dir), arch)
                # TODO: Also set site_packages_dir again so fry_eggs can work

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

        self.strip_libraries(arch)
        # self.fry_eggs(site_packages_dir)  # TODO uncomment this and make it work with python3
        super(SDL2GradleBootstrap, self).run_distribute()


bootstrap = SDL2GradleBootstrap()
