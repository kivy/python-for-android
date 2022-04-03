import sh
import os
import platform
from os.path import join, isdir, exists
from multiprocessing import cpu_count
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint
from pythonforandroid.util import current_directory, ensure_dir


class ICURecipe(Recipe):
    name = 'icu4c'
    version = '57.1'
    major_version = version.split('.')[0]
    url = (
        "https://github.com/unicode-org/icu/releases/download/"
        "release-{version_hyphen}/icu4c-{version_underscore}-src.tgz"
    )

    depends = ['hostpython3']  # installs in python
    patches = ['disable-libs-version.patch']

    built_libraries = {
        'libicui18n{}.so'.format(major_version): 'build_icu_android/lib',
        'libicuuc{}.so'.format(major_version): 'build_icu_android/lib',
        'libicudata{}.so'.format(major_version): 'build_icu_android/lib',
        'libicule{}.so'.format(major_version): 'build_icu_android/lib',
        'libicuio{}.so'.format(major_version): 'build_icu_android/lib',
        'libicutu{}.so'.format(major_version): 'build_icu_android/lib',
        'libiculx{}.so'.format(major_version): 'build_icu_android/lib',
    }

    @property
    def versioned_url(self):
        if self.url is None:
            return None
        return self.url.format(
            version=self.version,
            version_underscore=self.version.replace('.', '_'),
            version_hyphen=self.version.replace('.', '-'))

    def get_recipe_dir(self):
        """
        .. note:: We need to overwrite `Recipe.get_recipe_dir` due to the
                  mismatch name between the recipe's folder (icu) and the value
                  of `ICURecipe.name` (icu4c).
        """
        if self.ctx.local_recipes is not None:
            local_recipe_dir = join(self.ctx.local_recipes, 'icu')
            if exists(local_recipe_dir):
                return local_recipe_dir
        return join(self.ctx.root_dir, 'recipes', 'icu')

    def build_arch(self, arch):
        env = self.get_recipe_env(arch).copy()
        build_root = self.get_build_dir(arch.arch)

        def make_build_dest(dest):
            build_dest = join(build_root, dest)
            if not isdir(build_dest):
                ensure_dir(build_dest)
                return build_dest, False

            return build_dest, True

        icu_build = join(build_root, "icu_build")
        build_host, exists = make_build_dest("build_icu_host")

        host_env = os.environ.copy()
        # reduce the function set
        host_env["CPPFLAGS"] = (
            "-O3 -fno-short-wchar -DU_USING_ICU_NAMESPACE=1 -fno-short-enums "
            "-DU_HAVE_NL_LANGINFO_CODESET=0 -D__STDC_INT64__ -DU_TIMEZONE=0 "
            "-DUCONFIG_NO_LEGACY_CONVERSION=1 "
            "-DUCONFIG_NO_TRANSLITERATION=0 ")

        if not exists:
            icu4c_host_platform = platform.system()
            if icu4c_host_platform == "Darwin":
                icu4c_host_platform = "MacOSX"
            configure = sh.Command(
                join(build_root, "source", "runConfigureICU"))
            with current_directory(build_host):
                shprint(
                    configure,
                    icu4c_host_platform,
                    "--prefix="+icu_build,
                    "--enable-extras=no",
                    "--enable-strict=no",
                    "--enable-static=no",
                    "--enable-tests=no",
                    "--enable-samples=no",
                    _env=host_env)
                shprint(sh.make, "-j", str(cpu_count()), _env=host_env)
                shprint(sh.make, "install", _env=host_env)
        build_android, exists = make_build_dest("build_icu_android")
        if not exists:
            configure = sh.Command(join(build_root, "source", "configure"))

            with current_directory(build_android):
                shprint(
                    configure,
                    "--with-cross-build="+build_host,
                    "--enable-extras=no",
                    "--enable-strict=no",
                    "--enable-static=no",
                    "--enable-tests=no",
                    "--enable-samples=no",
                    "--host="+arch.command_prefix,
                    "--prefix="+icu_build,
                    _env=env)
                shprint(sh.make, "-j", str(cpu_count()), _env=env)
                shprint(sh.make, "install", _env=env)

    def install_libraries(self, arch):
        super().install_libraries(arch)

        src_include = join(
            self.get_build_dir(arch.arch), "icu_build", "include")
        dst_include = join(
            self.ctx.get_python_install_dir(arch.arch), "include", "icu")
        ensure_dir(dst_include)
        shprint(sh.cp, "-r", join(src_include, "layout"), dst_include)
        shprint(sh.cp, "-r", join(src_include, "unicode"), dst_include)


recipe = ICURecipe()
