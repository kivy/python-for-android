from pythonforandroid.recipe import Recipe, MesonRecipe
from pythonforandroid.logger import error
from os.path import join
import shutil

NUMPY_NDK_MESSAGE = "In order to build numpy, you must set minimum ndk api (minapi) to `24`.\n"


class NumpyRecipe(MesonRecipe):
    version = 'v1.26.5'
    url = 'git+https://github.com/numpy/numpy'
    hostpython_prerequisites = ["Cython>=3.0.6"]  # meson does not detects venv's cython
    extra_build_args = ['-Csetup-args=-Dblas=none', '-Csetup-args=-Dlapack=none']
    need_stl_shared = True

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        # Custom python is required, so that meson
        # gets libs and config files properly
        options["binaries"]["python"] = self.ctx.python_recipe.python_exe
        options["binaries"]["python3"] = self.ctx.python_recipe.python_exe
        options["properties"]["longdouble_format"] = "IEEE_DOUBLE_LE" if arch.arch in ["armeabi-v7a", "x86"] else "IEEE_QUAD_LE"
        return options

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        # _PYTHON_HOST_PLATFORM declares that we're cross-compiling
        # and avoids issues when building on macOS for Android targets.
        env["_PYTHON_HOST_PLATFORM"] = arch.command_prefix

        # NPY_DISABLE_SVML=1 allows numpy to build for non-AVX512 CPUs
        # See: https://github.com/numpy/numpy/issues/21196
        env["NPY_DISABLE_SVML"] = "1"
        env["TARGET_PYTHON_EXE"] = join(Recipe.get_recipe(
                "python3", self.ctx).get_build_dir(arch.arch), "android-build", "python")
        return env

    def download_if_necessary(self):
        # NumPy requires complex math functions which were added in api 24
        if self.ctx.ndk_api < 24:
            error(NUMPY_NDK_MESSAGE)
            exit(1)
        super().download_if_necessary()

    def build_arch(self, arch):
        super().build_arch(arch)
        self.restore_hostpython_prerequisites(["cython"])

    def get_hostrecipe_env(self, arch):
        env = super().get_hostrecipe_env(arch)
        env['RANLIB'] = shutil.which('ranlib')
        env["LDFLAGS"] += " -lm"
        return env


recipe = NumpyRecipe()
