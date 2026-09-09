import sh
from os.path import join, basename
from glob import glob
from multiprocessing import cpu_count
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint


class Panda3dRecipe(PyProjectRecipe):
    version = "1.10.14"
    url = "https://github.com/panda3d/panda3d/archive/refs/tags/v{version}.tar.gz"
    patches = ["makepanda.patch"]

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["ANDROID_NDK_ROOT"] = self.ctx.ndk_dir
        env["ANDROID_SDK_ROOT"] = self.ctx.sdk_dir
        env["ANDROID_TARGET_API"] = str(self.ctx.android_api)

        env["CXXFLAGS"] += " -stdlib=libstdc++ -Wno-unsupported-floating-point-opt"
        env["CFLAGS"] += " -Wno-unsupported-floating-point-opt"

        # Python includes
        python_includes = self.ctx.python_recipe.include_root(arch.arch)
        env["CXXFLAGS"] += " -I{}".format(python_includes)
        env["CFLAGS"] += " -I{}".format(python_includes)

        return env

    def build_arch(self, arch):
        self.install_hostpython_prerequisites()
        build_dir = self.get_build_dir(arch)
        env = self.get_recipe_env(arch)
        outputdir = join(build_dir, "dist")
        ensure_dir(outputdir)
        # Used by makepanda
        _arch = {
            "armeabi-v7a": "armv7a",
            "arm64-v8a": "aarch64",
            "x86": "x86",
            "x86_64": "x86_64",
        }[arch.arch]

        # Setup python lib folder
        panda3d_lib_dir = join(build_dir, "thirdparty/android-libs-{}".format(_arch), "python", "lib")
        ensure_dir(panda3d_lib_dir)
        for lib in glob(join(self.ctx.python_recipe.link_root(arch.arch), "*.so")):
            shprint(
                sh.ln, "-sf", lib, join(panda3d_lib_dir, basename(lib))
            )

        with current_directory(build_dir):
            shprint(
                sh.Command(self.hostpython_location),
                "makepanda/makepanda.py",
                "--everything",
                "--outputdir",
                outputdir,
                "--arch",
                _arch,
                "--target",
                "android-{}".format(self.ctx.ndk_api),
                "--threads",
                str(cpu_count()),
                "--wheel",
                _env=env
            )
        self.install_wheel(arch, join(build_dir, "dist", "*.whl"))


recipe = Panda3dRecipe()
