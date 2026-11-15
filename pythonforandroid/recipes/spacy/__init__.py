from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class SpacyRecipe(CompiledComponentsPythonRecipe):
    version = "3.8.7"
    url = "https://pypi.python.org/packages/source/s/spacy/spacy-{version}.tar.gz"
    site_packages_name = "spacy"
    depends = [
        "setuptools",
        "cython",
        # Explosion-provided dependencies
        "spacy-legacy",
        "spacy-loggers",
        "murmurhash",
        "cymem",
        "preshed",
        "thinc",
        "wasabi",
        "srsly",
        "catalogue",
        "weasel",
        "typer",
        "tqdm",
        "numpy",
        "requests",
        "pydantic",
        "jinja2",
        # Third party dependencies
        "confection",
        "packaging",
        "click",
        "typing_extensions",
        "shellingham",
        "rich",
        "markdown-it-py",
        "mdurl",
        "Pygments",
        "cloudpathlib",
        "smart-open",
        "wrapt",
        "markupsafe",
        # Official Python utilities
        "packaging",
        "langcodes",
        # # Required for Russian language
        # "pymorphy2",
        # "pymorphy2_dicts_ru",
        # "DAWG-Python",
        # "appdirs",
        # "pyparsing",
    ]
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        env["CXXFLAGS"] = env["CFLAGS"] + " -frtti -fexceptions"

        if with_flags_in_cc:
            env["CXX"] += " -frtti -fexceptions"

        env["LDFLAGS"] += f" -L{self.get_stl_library(arch)}"
        env["LIBS"] = env.get("LIBS", "") + f" -l{self.stl_lib_name}"
        return env

    def postbuild_arch(self, arch):
        super().postbuild_arch(arch)
        self.install_stl_lib(arch)


recipe = SpacyRecipe()
