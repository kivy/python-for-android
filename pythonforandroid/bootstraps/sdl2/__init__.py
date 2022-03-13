from pythonforandroid.toolchain import (
    Bootstrap, shprint, current_directory, info, info_main)
from pythonforandroid.util import ensure_dir
from os.path import join
import sh


class SDL2GradleBootstrap(Bootstrap):
    name = 'sdl2'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'sdl2'})
    )

    def assemble_distribution(self):
        info_main("# Creating Android project ({})".format(self.name))

        info("Copying SDL2/gradle build")
        shprint(sh.rm, "-rf", self.dist_dir)
        shprint(sh.cp, "-r", self.build_dir, self.dist_dir)

        # either the build use environment variable (ANDROID_HOME)
        # or the local.properties if exists
        with current_directory(self.dist_dir):
            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

        with current_directory(self.dist_dir):
            info("Copying Python distribution")

            self.distribute_javaclasses(self.ctx.javaclass_dir,
                                        dest_dir=join("src", "main", "java"))

            for arch in self.ctx.archs:
                python_bundle_dir = join(f'_python_bundle__{arch.arch}', '_python_bundle')
                ensure_dir(python_bundle_dir)

                self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
                site_packages_dir = self.ctx.python_recipe.create_python_bundle(
                    join(self.dist_dir, python_bundle_dir), arch)
                if not self.ctx.with_debug_symbols:
                    self.strip_libraries(arch)
                self.fry_eggs(site_packages_dir)

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

        super().assemble_distribution()


bootstrap = SDL2GradleBootstrap()
