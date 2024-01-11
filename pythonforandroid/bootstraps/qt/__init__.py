import sh
from os.path import join
from pythonforandroid.toolchain import (
    Bootstrap, current_directory, info, info_main, shprint)
from pythonforandroid.util import ensure_dir, rmdir


class QtBootstrap(Bootstrap):
    name = 'qt'
    recipe_depends = ['python3', 'genericndkbuild', 'PySide6', 'shiboken6']
    # this is needed because the recipes PySide6 and shiboken6 resides in the PySide Qt repository
    # - https://code.qt.io/cgit/pyside/pyside-setup.git/
    # Without this some tests will error because it cannot find the recipes within pythonforandroid
    # repository
    can_be_chosen_automatically = False

    def assemble_distribution(self):
        info_main("# Creating Android project using Qt bootstrap")

        rmdir(self.dist_dir)
        info("Copying gradle build")
        shprint(sh.cp, '-r', self.build_dir, self.dist_dir)

        with current_directory(self.dist_dir):
            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

        arch = self.ctx.archs[0]
        if len(self.ctx.archs) > 1:
            raise ValueError("Trying to build for more than one arch. Qt bootstrap cannot handle that yet")

        info(f"Bootstrap running with arch {arch}")

        with current_directory(self.dist_dir):
            info("Copying Python distribution")

            self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
            self.distribute_aars(arch)
            self.distribute_javaclasses(self.ctx.javaclass_dir,
                                        dest_dir=join("src", "main", "java"))

            python_bundle_dir = join(f'_python_bundle__{arch.arch}', '_python_bundle')
            ensure_dir(python_bundle_dir)
            site_packages_dir = self.ctx.python_recipe.create_python_bundle(
                join(self.dist_dir, python_bundle_dir), arch)

        if not self.ctx.with_debug_symbols:
            self.strip_libraries(arch)
        self.fry_eggs(site_packages_dir)
        super().assemble_distribution()


bootstrap = QtBootstrap()
