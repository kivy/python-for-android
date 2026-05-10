from pythonforandroid.recipe import PyProjectRecipe
from os.path import join


class VideoNativeRecipe(PyProjectRecipe):
    version = "1.0.0"
    url = "https://github.com/Novfensec/VideoNative/archive/{version}.zip"
    name = "videonative"
    site_packages_name = "videonative"

    hostpython_prerequisites = ["scikit-build-core", "pybind11", "cmake", "ninja"]
    depends = ["python3", "ffmpeg", "numpy"]

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        ffmpeg_recipe = self.get_recipe("ffmpeg", self.ctx)
        ffmpeg_build_dir = ffmpeg_recipe.get_build_dir(arch.arch)

        python_recipe = self.get_recipe("python3", self.ctx)
        py_include_dir = python_recipe.include_root(arch.arch)
        py_lib_file = join(
            python_recipe.get_build_dir(arch.arch),
            "android-build",
            f"libpython{python_recipe.major_minor_version_string}.so",
        )

        toolchain_file = join(
            self.ctx.ndk_dir, "build", "cmake", "android.toolchain.cmake"
        )

        env["SKBUILD_STRICT_CONFIG"] = "false"
        env["SKBUILD_CMAKE_ARGS"] = (
            f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file};"
            f"-DANDROID_ABI={arch.arch};"
            f"-DANDROID_PLATFORM=android-{self.ctx.ndk_api};"
            f"-DANDROID_FFMPEG_INCLUDE={join(ffmpeg_build_dir, 'include')};"
            f"-DANDROID_FFMPEG_LIB={join(ffmpeg_build_dir, 'lib')};"
            f"-DPython_EXECUTABLE={self.ctx.hostpython};"
            f"-DPython_INCLUDE_DIR={py_include_dir};"
            f"-DPython_LIBRARY={py_lib_file};"
        )

        return env


recipe = VideoNativeRecipe()
