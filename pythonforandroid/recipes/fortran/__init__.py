import os
import subprocess
import shutil
import sh
from pathlib import Path
from os.path import join
from pythonforandroid.recipe import Recipe
from pythonforandroid.recommendations import read_ndk_version
from pythonforandroid.logger import info, shprint, info_main
from pythonforandroid.util import ensure_dir
import hashlib

FLANG_FILES = {
    "package-flang-aarch64.tar.bz2": "bf01399513e3b435224d9a9f656b72a0965a23fdd8c3c26af0f7c32f2a5f3403",
    "package-flang-host.tar.bz2": "3ea2c0e8125ededddf9b3f23c767b8e37816e140ac934c76ace19a168fefdf83",
    "package-flang-x86_64.tar.bz2": "afe7e391355c71e7b0c8ee71a3002e83e2e524ad61810238815facf3030be6e6",
    "package-install.tar.bz2": "169b75f6125dc7b95e1d30416147a05d135da6cbe9cc8432d48f5b8633ac38db",
}


class GFortranRecipe(Recipe):
    # flang support in NDK by @termux (on github)
    name = "fortran"
    toolchain_ver = 0
    url = "https://github.com/termux/ndk-toolchain-clang-with-flang/releases/download/"

    def match_sha256(self, file_path, expected_hash):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        file_hash = sha256.hexdigest()
        return file_hash == expected_hash

    @property
    def ndk_version(self):
        ndk_version = read_ndk_version(self.ctx.ndk_dir)
        minor_to_letter = {0: ""}
        minor_to_letter.update(
            {n + 1: chr(i) for n, i in enumerate(range(ord("b"), ord("b") + 25))}
        )
        return f"{ndk_version.major}{minor_to_letter[ndk_version.minor]}"

    def get_cache_dir(self):
        dir_name = self.get_dir_name()
        return join(self.ctx.build_dir, "other_builds", dir_name)

    def get_fortran_dir(self):
        toolchain_name = f"android-r{self.ndk_version}-api-{self.ctx.ndk_api}"
        return join(
            self.get_cache_dir(), f"{toolchain_name}-flang-v{self.toolchain_ver}"
        )

    def get_incomplete_files(self):
        incomplete_files = []
        cache_dir = self.get_cache_dir()
        for file, sha256sum in FLANG_FILES.items():
            _file = join(cache_dir, file)
            if not (os.path.exists(_file) and self.match_sha256(_file, sha256sum)):
                incomplete_files.append(file)
        return incomplete_files

    def download_if_necessary(self):
        assert self.ndk_version == "28c"
        if len(self.get_incomplete_files()) == 0:
            return
        self.download()

    def download(self):
        cache_dir = self.get_cache_dir()
        ensure_dir(cache_dir)
        for file in self.get_incomplete_files():
            _file = join(cache_dir, file)
            if os.path.exists(_file):
                os.remove(_file)
            self.download_file(f"{self.url}r{join(self.ndk_version, file)}", _file)

    def extract_tar(self, file_path: Path, dest: Path, strip=1):
        shprint(
            sh.tar,
            "xf",
            str(file_path),
            "--strip-components",
            str(strip),
            "-C",
            str(dest) if dest else ".",
        )

    def create_flang_wrapper(self, path: Path, target: str):
        script = f"""#!/usr/bin/env bash
if [ "$1" != "-cpp" ] && [ "$1" != "-fc1" ]; then
  `dirname $0`/flang-new --target={target}{self.ctx.ndk_api} -D__ANDROID_API__={self.ctx.ndk_api} "$@"
else
  `dirname $0`/flang-new "$@"
fi
"""
        path.write_text(script)
        path.chmod(0o755)

    def unpack(self, arch):
        info_main("Unpacking fortran")

        flang_folder = self.get_fortran_dir()
        if os.path.exists(flang_folder):
            info("{} is already unpacked, skipping".format(self.name))
            return

        toolchain_path = Path(
            join(self.ctx.ndk_dir, "toolchains/llvm/prebuilt/linux-x86_64")
        )
        cache_dir = Path(os.path.abspath(self.get_cache_dir()))

        # clean tmp folder
        tmp_folder = Path(os.path.abspath(f"{flang_folder}-tmp"))
        shutil.rmtree(tmp_folder, ignore_errors=True)
        tmp_folder.mkdir(parents=True)
        os.chdir(tmp_folder)

        self.extract_tar(cache_dir / "package-install.tar.bz2", None, strip=4)
        self.extract_tar(cache_dir / "package-flang-host.tar.bz2", None)

        sysroot_path = tmp_folder / "sysroot"
        shutil.copytree(toolchain_path / "sysroot", sysroot_path)

        self.extract_tar(
            cache_dir / "package-flang-aarch64.tar.bz2",
            sysroot_path / "usr/lib/aarch64-linux-android",
        )
        self.extract_tar(
            cache_dir / "package-flang-x86_64.tar.bz2",
            sysroot_path / "usr/lib/x86_64-linux-android",
        )

        # Fix lib/clang paths
        version_output = subprocess.check_output(
            [str(tmp_folder / "bin/clang"), "--version"], text=True
        )
        clang_version = next(
            (line for line in version_output.splitlines() if "clang version" in line),
            "",
        )
        major_ver = clang_version.split("clang version ")[-1].split(".")[0]

        lib_path = tmp_folder / f"lib/clang/{major_ver}/lib"
        src_lib_path = toolchain_path / f"lib/clang/{major_ver}/lib"
        shutil.rmtree(lib_path, ignore_errors=True)
        lib_path.mkdir(parents=True)

        for item in src_lib_path.iterdir():
            shprint(sh.cp, "-r", str(item), str(lib_path))

        # Create flang wrappers
        targets = [
            "aarch64-linux-android",
            "armv7a-linux-androideabi",
            "i686-linux-android",
            "x86_64-linux-android",
        ]

        for target in targets:
            wrapper_path = tmp_folder / f"bin/{target}-flang"
            self.create_flang_wrapper(wrapper_path, target)
            shutil.copy(
                wrapper_path, tmp_folder / f"bin/{target}{self.ctx.ndk_api}-flang"
            )

        tmp_folder.rename(flang_folder)

    @property
    def bin_path(self):
        return f"{self.get_fortran_dir()}/bin"

    def get_host_platform(self, arch):
        return {
            "arm64-v8a": "aarch64-linux-android",
            "armeabi-v7a": "armv7a-linux-androideabi",
            "x86_64": "x86_64-linux-android",
            "x86": "i686-linux-android",
        }[arch]

    def get_fortran_bin(self, arch):
        return join(self.bin_path, f"{self.get_host_platform(arch)}-flang")

    def get_fortran_flags(self, arch):
        return f"--target={self.get_host_platform(arch)}{self.ctx.ndk_api} -D__ANDROID_API__={self.ctx.ndk_api}"


recipe = GFortranRecipe()
