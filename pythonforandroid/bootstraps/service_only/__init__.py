import sh
from os.path import join
from pythonforandroid.toolchain import (
    Bootstrap, current_directory, info, info_main, shprint)
from pythonforandroid.util import ensure_dir


class ServiceOnlyBootstrap(Bootstrap):

    name = 'service_only'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'genericndkbuild'})
    )

    def assemble_distribution(self):
        info_main('# Creating Android project from build and {} bootstrap'.format(
            self.name))

        info('This currently just copies the build stuff straight from the build dir.')
        shprint(sh.rm, '-rf', self.dist_dir)
        shprint(sh.cp, '-r', self.build_dir, self.dist_dir)
        with current_directory(self.dist_dir):
            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

        with current_directory(self.dist_dir):
            info('Copying python distribution')

            self.distribute_javaclasses(self.ctx.javaclass_dir,
                                        dest_dir=join("src", "main", "java"))

            for arch in self.ctx.archs:
                self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
                self.distribute_aars(arch)

                python_bundle_dir = join(f'_python_bundle__{arch.arch}', '_python_bundle')
                ensure_dir(python_bundle_dir)
                site_packages_dir = self.ctx.python_recipe.create_python_bundle(
                    join(self.dist_dir, python_bundle_dir), arch)
                if not self.ctx.with_debug_symbols:
                    self.strip_libraries(arch)
                self.fry_eggs(site_packages_dir)

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

        super().assemble_distribution()


bootstrap = ServiceOnlyBootstrap()
