import shutil
from os.path import join

from pythonforandroid.recipe import PyProjectRecipe


class MpvRecipe(PyProjectRecipe):
    name = "mpv"
    version = "1.0.8"
    url = "https://pypi.io/packages/source/p/python-mpv/python_mpv-{version}.tar.gz"
    depends = ["python3", "libmpv"]
    patches = ["android.patch"]

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        shutil.copyfile(
            join(self.get_recipe_dir(), "mpv_android.py"),
            join(self.get_build_dir(arch.arch), "mpv_android.py"),
        )


recipe = MpvRecipe()
