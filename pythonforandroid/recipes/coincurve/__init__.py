import os
from pythonforandroid.recipe import PythonRecipe


class CoincurveRecipe(PythonRecipe):
    version = "19.0.1"
    url = "https://github.com/ofek/coincurve/archive/v{version}.tar.gz"
    call_hostpython_via_targetpython = False
    depends = ["setuptools", "libffi", "cffi", "libsecp256k1", "asn1crypto"]
    patches = ["coincurve.patch"]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(CoincurveRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        libsecp256k1 = self.get_recipe("libsecp256k1", self.ctx)
        libsecp256k1_dir = libsecp256k1.get_build_dir(arch.arch)
        env["CFLAGS"] += " -I" + os.path.join(libsecp256k1_dir, "include")
        env["LDFLAGS"] += " -lsecp256k1"
        return env


recipe = CoincurveRecipe()
