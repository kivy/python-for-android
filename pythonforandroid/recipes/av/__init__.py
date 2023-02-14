from pythonforandroid.toolchain import Recipe
from pythonforandroid.recipe import CythonRecipe


class PyAVRecipe(CythonRecipe):

    name = "av"
    version = "10.0.0"
    url = "https://github.com/PyAV-Org/PyAV/archive/v{version}.zip"

    depends = ["python3", "cython", "ffmpeg", "av_codecs"]
    opt_depends = ["openssl"]

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch)

        build_dir = Recipe.get_recipe("ffmpeg", self.ctx).get_build_dir(
            arch.arch
        )
        self.setup_extra_args = ["--ffmpeg-dir={}".format(build_dir)]

        return env


recipe = PyAVRecipe()
