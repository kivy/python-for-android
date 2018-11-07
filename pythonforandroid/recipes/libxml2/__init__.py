from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh


class Libxml2Recipe(Recipe):
    version = "2.7.8"
    url = "http://xmlsoft.org/sources/libxml2-{version}.tar.gz"
    depends = []
    patches = ["add-glob.c.patch"]

    def should_build(self, arch):
        super(Libxml2Recipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), "libxml2.a"))

    def build_arch(self, arch):
        super(Libxml2Recipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            env["CC"] += " -I%s" % self.get_build_dir(arch.arch)
            shprint(
                sh.Command("./configure"),
                "--host=arm-linux-eabi",
                "--without-modules",
                "--without-legacy",
                "--without-history",
                "--without-debug",
                "--without-docbook",
                "--without-python",
                "--without-threads",
                "--without-iconv",
                _env=env,
            )

            # Ensure we only build libxml2.la as if we do everything
            # we'll need the glob dependency which is a big headache
            shprint(sh.make, "libxml2.la", _env=env)
            shutil.copyfile(
                ".libs/libxml2.a", join(self.ctx.get_libs_dir(arch.arch), "libxml2.a")
            )

    def get_recipe_env(self, arch):
        env = super(Libxml2Recipe, self).get_recipe_env(arch)
        env["CONFIG_SHELL"] = "/bin/bash"
        env["SHELL"] = "/bin/bash"
        env[
            "CC"
        ] = "arm-linux-androideabi-gcc -DANDROID -mandroid -fomit-frame-pointer --sysroot={}".format(
            self.ctx.ndk_platform
        )
        return env


recipe = Libxml2Recipe()
