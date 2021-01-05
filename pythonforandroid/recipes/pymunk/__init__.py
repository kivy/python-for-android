from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class PymunkRecipe(CompiledComponentsPythonRecipe):
    name = "pymunk"
    version = "6.0.0"
    url = "https://pypi.python.org/packages/source/p/pymunk/pymunk-{version}.zip"
    depends = ["cffi", "setuptools"]
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["LDFLAGS"] += " -llog"  # Used by Chipmunk cpMessage
        env["LDFLAGS"] += " -lm"  # For older versions of Android
        return env


recipe = PymunkRecipe()
