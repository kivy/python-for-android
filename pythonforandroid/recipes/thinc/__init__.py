from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class ThincRecipe(CompiledComponentsPythonRecipe):
    version = "8.3.4"
    url = "https://pypi.python.org/packages/source/t/thinc/thinc-{version}.tar.gz"
    site_packages_name = "thinc"
    depends = [
        "setuptools",
        "cython",
        # Explosion-provided dependencies
        "murmurhash",
        "cymem",
        "preshed",
        "blis",
        "srsly",
        "wasabi",
        "catalogue",
        "confection",
        "numpy",
        "pydantic",
        "packaging",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

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


recipe = ThincRecipe()
