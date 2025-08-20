from pythonforandroid.recipe import PythonRecipe
from os.path import join


class Pybind11Recipe(PythonRecipe):
    """
    Recipe to build pybind11 for Android using cmake.
    """

    version = "2.11.1"
    url = "https://github.com/pybind/pybind11/archive/refs/tags/v{version}.zip"

    # Make sure we depend on setuptools and cmake
    depends = ["setuptools", "cmake"]
    # Don’t let p4a try to run setup.py through targetpython
    call_hostpython_via_targetpython = False
    # Install into hostpython, because pybind11 is a header-only lib
    install_in_hostpython = True

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # Ensure cmake is found inside hostpython
        env["PATH"] = "/usr/bin:" + env.get("PATH", "")
        return env

    def get_include_dir(self, arch):
        """
        Return the directory where pybind11 headers will be located.
        """
        return join(self.get_build_dir(arch.arch), "include")


recipe = Pybind11Recipe()
