from pythonforandroid.toolchain import (
    Bootstrap, shprint, current_directory, info, info_main)
from pythonforandroid.util import ensure_dir
from os.path import join, exists
import sh


class SDL2GradleBootstrap(Bootstrap):
    name = 'sdl2'

    recipe_depends = ['sdl2', ('python2', 'python3', 'python3crystax')]

    def run_distribute(self):
        info_main("# Creating Android project ({})".format(self.name))

        arch = self.ctx.archs[0]
        python_install_dir = self.ctx.get_python_install_dir()
        from_crystax = self.ctx.python_recipe.from_crystax

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

        with current_directory(self.dist_dir):
            info("Copying Python distribution")

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

            python_bundle_dir = join('_python_bundle', '_python_bundle')
            if 'python2' in self.ctx.recipe_build_order:
                # Python 2 is a special case with its own packaging location
                python_bundle_dir = 'private'
            ensure_dir(python_bundle_dir)

            site_packages_dir = self.ctx.python_recipe.create_python_bundle(
                join(self.dist_dir, python_bundle_dir), arch)

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

        self.strip_libraries(arch)
        self.fry_eggs(site_packages_dir)
        super(SDL2GradleBootstrap, self).run_distribute()


bootstrap = SDL2GradleBootstrap()
