from os.path import join

from pythonforandroid.toolchain import Bootstrap
from pythonforandroid.util import ensure_dir


class SDLGradleBootstrap(Bootstrap):
    name = "_sdl_common"

    recipe_depends = []

    def _assemble_distribution_for_arch(self, arch):
        """SDL bootstrap skips distribute_aars() - handled differently."""
        self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
        # Note: SDL bootstrap does not call distribute_aars()

        python_bundle_dir = join(f'_python_bundle__{arch.arch}', '_python_bundle')
        ensure_dir(python_bundle_dir)
        site_packages_dir = self.ctx.python_recipe.create_python_bundle(
            join(self.dist_dir, python_bundle_dir), arch)
        if not self.ctx.with_debug_symbols:
            self.strip_libraries(arch)
        self.fry_eggs(site_packages_dir)
