from os.path import join
from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class PyICURecipe(CppCompiledComponentsPythonRecipe):
    version = '1.9.2'
    url = ('https://pypi.python.org/packages/source/P/PyICU/'
           'PyICU-{version}.tar.gz')
    depends = ["icu"]
    patches = ['locale.patch']

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        icu_include = join(
            self.ctx.get_python_install_dir(), "include", "icu")

        icu_recipe = self.get_recipe('icu', self.ctx)
        icu_link_libs = icu_recipe.built_libraries.keys()
        env["PYICU_LIBRARIES"] = ":".join(lib[3:-3] for lib in icu_link_libs)
        env["CPPFLAGS"] += " -I" + icu_include
        env["LDFLAGS"] += " -L" + join(
            icu_recipe.get_build_dir(arch.arch), "icu_build", "lib"
        )

        return env


recipe = PyICURecipe()
