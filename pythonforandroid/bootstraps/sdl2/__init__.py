from pythonforandroid.toolchain import (
    Bootstrap, shprint, current_directory, info, info_main)
from pythonforandroid.util import ensure_dir
from os.path import join
import sh


class SDL2GradleBootstrap(Bootstrap):
    name = 'sdl2'

    recipe_depends = ['sdl2', ('python2', 'python3', 'python3crystax')]

    libraries_to_load = ['SDL2', 'SDL2_image', 'SDL2_mixer', 'SDL2_ttf']

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

            self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
            self.distribute_javaclasses(self.ctx.javaclass_dir,
                                        dest_dir=join("src", "main", "java"))

            python_bundle_dir = join('_python_bundle', '_python_bundle')
            ensure_dir(python_bundle_dir)

            site_packages_dir = self.ctx.python_recipe.create_python_bundle(
                join(self.dist_dir, python_bundle_dir), arch)

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

            # collect libs to load by android os at runtime
            libs = self.collect_libraries_to_load(arch)
            target_file = join('src', 'main', 'assets', 'libraries_to_load.txt')
            with open(target_file, 'a') as libs_file:
                for lib in libs:
                    libs_file.write(lib + '\n')

        self.strip_libraries(arch)
        self.fry_eggs(site_packages_dir)
        super(SDL2GradleBootstrap, self).run_distribute()


bootstrap = SDL2GradleBootstrap()
