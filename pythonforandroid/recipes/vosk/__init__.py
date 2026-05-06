from os.path import basename, dirname, exists, join
import zipfile

from pythonforandroid.logger import info
from pythonforandroid.recipe import PythonRecipe, current_directory, shprint
from pythonforandroid.util import BuildInterruptingException, ensure_dir


class VoskRecipe(PythonRecipe):
    version = "0.3.45"
    url = "https://github.com/alphacep/vosk-api/archive/refs/tags/v{version}.tar.gz"
    site_packages_name = "vosk"
    depends = ["cffi"]
    python_depends = ["requests", "tqdm", "srt", "websockets"]
    hostpython_prerequisites = [
        "setuptools",
        "wheel",
        "cffi",
        "requests",
        "tqdm",
        "srt",
        "websockets",
    ]
    call_hostpython_via_targetpython = False

    android_aar_url = (
        "https://repo.maven.apache.org/maven2/com/alphacephei/"
        "vosk-android/{version}/vosk-android-{version}.aar"
    )
    android_aar_abis = {
        "arm64-v8a": "arm64-v8a",
        "armeabi-v7a": "armeabi-v7a",
        "x86": "x86",
        "x86_64": "x86_64",
    }

    def build_arch(self, arch):
        self.install_hostpython_prerequisites()

        env = self.get_recipe_env(arch)
        python_dir = join(self.get_build_dir(arch.arch), "python")
        install_dir = self.ctx.get_python_install_dir(arch.arch)

        info("Installing Vosk Python bindings into site-packages")
        with current_directory(python_dir):
            shprint(
                self._host_recipe.pip,
                "install",
                ".",
                "--compile",
                "--no-deps",
                "--target",
                install_dir,
                _env=env,
            )

        self.install_android_libvosk(arch)

    def install_android_libvosk(self, arch):
        aar_abi = self.android_aar_abis.get(arch.arch)
        if aar_abi is None:
            supported = ", ".join(sorted(self.android_aar_abis))
            raise BuildInterruptingException(
                f"Vosk does not provide an Android library for {arch.arch}. "
                f"Supported ABIs: {supported}"
            )

        aar_path = self.download_android_aar()
        aar_lib_path = f"jni/{aar_abi}/libvosk.so"
        target_path = join(
            self.ctx.get_python_install_dir(arch.arch),
            self.site_packages_name,
            "libvosk.so",
        )
        ensure_dir(dirname(target_path))

        info(f"Installing Android {arch.arch} libvosk.so")
        try:
            with zipfile.ZipFile(aar_path) as aar:
                with aar.open(aar_lib_path) as source, open(target_path, "wb") as target:
                    target.write(source.read())
        except KeyError as exc:
            raise BuildInterruptingException(
                f"{basename(aar_path)} does not contain {aar_lib_path}"
            ) from exc

    def download_android_aar(self):
        aar_dir = join(self.ctx.packages_path, "vosk-android")
        ensure_dir(aar_dir)

        aar_name = f"vosk-android-{self.version}.aar"
        aar_path = join(aar_dir, aar_name)
        if not exists(aar_path):
            self.download_file(
                self.android_aar_url.format(version=self.version),
                aar_name,
                cwd=aar_dir,
            )
        return aar_path


recipe = VoskRecipe()
