from pythonforandroid.recipe import Recipe, CompiledComponentsPythonRecipe
from os.path import exists, join
from os import uname


class LXMLRecipe(CompiledComponentsPythonRecipe):
    version = '4.8.0'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'  # noqa
    depends = ['librt', 'libxml2', 'libxslt', 'setuptools']
    name = 'lxml'

    call_hostpython_via_targetpython = False  # Due to setuptools

    def should_build(self, arch):
        super().should_build(arch)

        py_ver = self.ctx.python_recipe.major_minor_version_string
        build_platform = "{system}-{machine}".format(
            system=uname()[0], machine=uname()[-1]
        ).lower()
        build_dir = join(
            self.get_build_dir(arch.arch),
            "build",
            "lib." + build_platform + "-" + py_ver,
            "lxml",
        )
        py_libs = ["_elementpath.so", "builder.so", "etree.so", "objectify.so"]

        return not all([exists(join(build_dir, lib)) for lib in py_libs])

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # libxslt flags
        libxslt_recipe = Recipe.get_recipe('libxslt', self.ctx)
        libxslt_build_dir = libxslt_recipe.get_build_dir(arch.arch)

        # libxml2 flags
        libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)
        libxml2_build_dir = libxml2_recipe.get_build_dir(arch.arch)

        env["STATIC"] = "true"

        env["LXML_STATIC_INCLUDE_DIRS"] = "{}:{}".format(
            join(libxml2_build_dir, "include"), join(libxslt_build_dir)
        )
        env["LXML_STATIC_LIBRARY_DIRS"] = "{}:{}:{}".format(
            join(libxml2_build_dir, ".libs"),
            join(libxslt_build_dir, "libxslt", ".libs"),
            join(libxslt_build_dir, "libexslt", ".libs"),
        )

        env["WITH_XML2_CONFIG"] = join(libxml2_build_dir, "xml2-config")
        env["WITH_XSLT_CONFIG"] = join(libxslt_build_dir, "xslt-config")

        env["LXML_STATIC_BINARIES"] = "{}:{}:{}".format(
            join(libxml2_build_dir, ".libs", "libxml2.a"),
            join(libxslt_build_dir, "libxslt", ".libs", "libxslt.a"),
            join(libxslt_build_dir, "libexslt", ".libs", "libexslt.a"),
        )

        return env


recipe = LXMLRecipe()
