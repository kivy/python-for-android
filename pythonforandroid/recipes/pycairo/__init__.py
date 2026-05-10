from pythonforandroid.recipe import MesonRecipe
from os.path import join


class PyCairoRecipe(MesonRecipe):
    version = '1.28.0'
    url = 'https://github.com/pygobject/pycairo/releases/download/v{version}/pycairo-{version}.tar.gz'
    name = 'pycairo'
    site_packages_name = 'cairo'
    depends = ['libcairo']
    patches = ["meson.patch"]

    def build_arch(self, arch):

        include_path = join(self.get_recipe('libcairo', self.ctx).get_build_dir(arch), "install", "include", "cairo")
        lib_path = self.ctx.get_libs_dir(arch.arch)

        self.extra_build_args += [
            f'-Csetup-args=-Dcairo_include={include_path}',
            f'-Csetup-args=-Dcairo_lib={lib_path}',
        ]

        super().build_arch(arch)


recipe = PyCairoRecipe()
