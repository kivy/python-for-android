import sys
import os
import shutil
from os.path import join, exists, basename
import sh
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint, current_directory
from pythonforandroid.util import ensure_dir


class SkiaRecipe(Recipe):
    version = "skia-binaries-m140-rev1.a0"
    url = "https://github.com/DexerBR/skia-builder/releases/download/{version}/android-merged.tar.gz"
    name = "skia"

    skia_libraries = [
        "libskparagraph.a",
        "libskia.a",
        "libskottie.a",
        "libsksg.a",
        "libskshaper.a",
        "libskunicode_icu.a",
        "libskunicode_core.a",
        "libjsonreader.a",
    ]

    built_libraries = {"libskmerged.a": "bin"}

    def _get_skia_platform(self, arch):
        arch_map = {
            "arm64-v8a": "android-arm64",
            "armeabi-v7a": "android-arm",
            "x86_64": "android-x64",
            "x86": "android-x86",
        }
        arch_name = arch.arch if hasattr(arch, "arch") else arch
        return arch_map.get(arch_name, arch_name)

    def unpack(self, arch):
        build_dir = self.get_build_container_dir(arch)
        target_dir = self.get_build_dir(arch)

        if exists(target_dir):
            return

        ensure_dir(build_dir)

        filename = basename(self.versioned_url)
        archive_path = join(self.ctx.packages_path, self.name, filename)
        skia_platform = self._get_skia_platform(arch)

        with current_directory(build_dir):
            temp_extract_dir = join(build_dir, "temp_extract")
            ensure_dir(temp_extract_dir)

            with current_directory(temp_extract_dir):
                shprint(sh.tar, "xzf", archive_path)

            ensure_dir(target_dir)

            # Find and extract the architecture-specific tar.gz
            arch_file = f"{skia_platform}.tar.gz"
            arch_file_path = join(temp_extract_dir, arch_file)

            if exists(arch_file_path):
                print(f"Found {arch_file}, extracting...")
                with current_directory(target_dir):
                    shprint(sh.tar, "xzf", arch_file_path)
            else:
                print(f"Architecture file not found: {arch_file}")
                print(f"Available files: {os.listdir(temp_extract_dir)}")
                sys.exit(1)

            shutil.rmtree(temp_extract_dir)

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        merged_lib_path = join(build_dir, "bin", "libskmerged.a")

        lib_files = []
        for lib in self.skia_libraries:
            lib_path = join(build_dir, "bin", lib)
            if exists(lib_path):
                lib_files.append(lib_path)

        if lib_files:
            with current_directory(build_dir):
                shprint(
                    sh.Command(self.ctx.ndk.llvm_ar),
                    "rcs",
                    merged_lib_path,
                    *lib_files,
                )

    def get_include_dirs(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return [
            d
            for d in [
                join(build_dir, subdir)
                for subdir in ["include", "modules", "src"]
            ]
            if exists(d)
        ]

    def get_lib_dir(self, arch):
        return self.get_build_dir(arch.arch)


recipe = SkiaRecipe()
