from pythonforandroid.toolchain import Recipe, shutil
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import exists, join
from os import listdir


class LXMLRecipe(CompiledComponentsPythonRecipe):
    version = "3.6.0"
    url = "https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz"
    depends = ["libxml2", "libxslt"]
    name = "lxml"

    call_hostpython_via_targetpython = False  # Due to setuptools

    def should_build(self, arch):
        super(LXMLRecipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), "etree.so"))

    def build_arch(self, arch):
        super(LXMLRecipe, self).build_arch(arch)

        def get_lib_build_dir_name():
            for f in listdir(join(self.get_build_dir(arch.arch), "build")):
                if f.startswith("lib.linux-x86_64"):
                    return f
            return None

        def get_so_name(so_target, dirpath):
            for f in listdir(dirpath):
                if f.startswith(so_target.partition(".")[0] + ".") and \
                        f.endswith(".so"):
                    return join(dirpath, f)
            return None

        so_origin_dir = "%s/build/%s/lxml/" % (self.get_build_dir(arch.arch),
                                               get_lib_build_dir_name())
        shutil.copyfile(
            join(so_origin_dir, get_so_name("etree.so", so_origin_dir)),
            join(self.ctx.get_libs_dir(arch.arch), "etree.so"),
        )
        shutil.copyfile(
            join(so_origin_dir, get_so_name("objectify.so", so_origin_dir)),
            join(self.ctx.get_libs_dir(arch.arch), "objectify.so"),
        )

    def get_recipe_env(self, arch):
        env = super(LXMLRecipe, self).get_recipe_env(arch)
        libxslt_recipe = Recipe.get_recipe("libxslt", self.ctx).get_build_dir(arch.arch)
        libxml2_recipe = Recipe.get_recipe("libxml2", self.ctx).get_build_dir(arch.arch)
        env["CC"] += " -I%s/include -I%s " % (
            libxml2_recipe,
            libxslt_recipe,
        )
        return env


recipe = LXMLRecipe()
