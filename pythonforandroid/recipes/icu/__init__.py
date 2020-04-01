import sh
import os
from os.path import join, isdir
from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import shprint
from pythonforandroid.util import current_directory, ensure_dir


class ICURecipe(NDKRecipe):
    name = 'icu4c'
    version = '57.1'
    url = 'http://download.icu-project.org/files/icu4c/57.1/icu4c-57_1-src.tgz'

    depends = [('hostpython2', 'hostpython3')]  # installs in python
    generated_libraries = [
        'libicui18n.so', 'libicuuc.so', 'libicudata.so', 'libicule.so']

    def get_lib_dir(self, arch):
        lib_dir = join(self.ctx.get_python_install_dir(), "lib")
        ensure_dir(lib_dir)
        return lib_dir

    def prepare_build_dir(self, arch):
        if self.ctx.android_api > 19:
            # greater versions do not have /usr/include/sys/exec_elf.h
            raise RuntimeError("icu needs an android api <= 19")

        super(ICURecipe, self).prepare_build_dir(arch)

    def build_arch(self, arch, *extra_args):
        env = self.get_recipe_env(arch).copy()
        build_root = self.get_build_dir(arch.arch)

        def make_build_dest(dest):
            build_dest = join(build_root, dest)
            if not isdir(build_dest):
                ensure_dir(build_dest)
                return build_dest, False

            return build_dest, True

        icu_build = join(build_root, "icu_build")
        build_linux, exists = make_build_dest("build_icu_linux")

        host_env = os.environ.copy()
        # reduce the function set
        host_env["CPPFLAGS"] = (
            "-O3 -fno-short-wchar -DU_USING_ICU_NAMESPACE=1 -fno-short-enums "
            "-DU_HAVE_NL_LANGINFO_CODESET=0 -D__STDC_INT64__ -DU_TIMEZONE=0 "
            "-DUCONFIG_NO_LEGACY_CONVERSION=1 "
            "-DUCONFIG_NO_TRANSLITERATION=0 ")

        if not exists:
            configure = sh.Command(
                join(build_root, "source", "runConfigureICU"))
            with current_directory(build_linux):
                shprint(
                    configure,
                    "Linux",
                    "--prefix="+icu_build,
                    "--enable-extras=no",
                    "--enable-strict=no",
                    "--enable-static",
                    "--enable-tests=no",
                    "--enable-samples=no",
                    _env=host_env)
                shprint(sh.make, "-j5", _env=host_env)
                shprint(sh.make, "install", _env=host_env)

        build_android, exists = make_build_dest("build_icu_android")
        if not exists:

            configure = sh.Command(join(build_root, "source", "configure"))

            include = (
                " -I{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/include/"
                " -I{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/libs/"
                "{arch}/include")
            include = include.format(ndk=self.ctx.ndk_dir,
                                     version=env["TOOLCHAIN_VERSION"],
                                     arch=arch.arch)
            env["CPPFLAGS"] = env["CXXFLAGS"] + " "
            env["CPPFLAGS"] += host_env["CPPFLAGS"]
            env["CPPFLAGS"] += include

            lib = "{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/libs/{arch}"
            lib = lib.format(ndk=self.ctx.ndk_dir,
                             version=env["TOOLCHAIN_VERSION"],
                             arch=arch.arch)
            env["LDFLAGS"] += " -lgnustl_shared -L"+lib

            env.pop("CFLAGS", None)
            env.pop("CXXFLAGS", None)

            with current_directory(build_android):
                shprint(
                    configure,
                    "--with-cross-build="+build_linux,
                    "--enable-extras=no",
                    "--enable-strict=no",
                    "--enable-static",
                    "--enable-tests=no",
                    "--enable-samples=no",
                    "--host="+env["TOOLCHAIN_PREFIX"],
                    "--prefix="+icu_build,
                    _env=env)
                shprint(sh.make, "-j5", _env=env)
                shprint(sh.make, "install", _env=env)

        self.copy_files(arch)

    def copy_files(self, arch):
        env = self.get_recipe_env(arch)

        lib = "{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/libs/{arch}"
        lib = lib.format(ndk=self.ctx.ndk_dir,
                         version=env["TOOLCHAIN_VERSION"],
                         arch=arch.arch)
        stl_lib = join(lib, "libgnustl_shared.so")
        dst_dir = join(self.ctx.get_site_packages_dir(), "..", "lib-dynload")
        shprint(sh.cp, stl_lib, dst_dir)

        src_lib = join(self.get_build_dir(arch.arch), "icu_build", "lib")
        dst_lib = self.get_lib_dir(arch)

        src_suffix = "." + self.version
        dst_suffix = "." + self.version.split(".")[0]  # main version
        for lib in self.generated_libraries:
            shprint(sh.cp, join(src_lib, lib+src_suffix),
                    join(dst_lib, lib+dst_suffix))

        src_include = join(
            self.get_build_dir(arch.arch), "icu_build", "include")
        dst_include = join(
            self.ctx.get_python_install_dir(), "include", "icu")
        ensure_dir(dst_include)
        shprint(sh.cp, "-r", join(src_include, "layout"), dst_include)
        shprint(sh.cp, "-r", join(src_include, "unicode"), dst_include)

        # copy stl library
        lib = "{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/libs/{arch}"
        lib = lib.format(ndk=self.ctx.ndk_dir,
                         version=env["TOOLCHAIN_VERSION"],
                         arch=arch.arch)
        stl_lib = join(lib, "libgnustl_shared.so")

        dst_dir = join(self.ctx.get_python_install_dir(), "lib")
        ensure_dir(dst_dir)
        shprint(sh.cp, stl_lib, dst_dir)


recipe = ICURecipe()
