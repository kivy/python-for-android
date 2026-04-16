from pythonforandroid.toolchain import Recipe
from pythonforandroid.recipe import PyProjectRecipe


class PyAVRecipe(PyProjectRecipe):

    name = "av"
    version = "17.0.0"
    url = "https://github.com/PyAV-Org/PyAV/archive/v{version}.zip"
    depends = ["python3", "ffmpeg", "av_codecs", "openssl"]
    hostpython_prerequisites = ["cython>=3.1.0"]

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch)
        build_dir = Recipe.get_recipe("ffmpeg", self.ctx).get_build_dir(arch.arch)
        env["CFLAGS"] += f" -I{build_dir}"
        self.extra_build_args += ["--config-setting=--ffmpeg-dir={}".format(build_dir)]
        return env


recipe = PyAVRecipe()
