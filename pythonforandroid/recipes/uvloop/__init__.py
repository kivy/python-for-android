from pythonforandroid.recipe import PythonRecipe


class UvloopRecipe(PythonRecipe):
    # 0.19.0
    version = '6c770dc3fbdd281d15c2ad46588c139696f9269c'
    url = 'git+https://github.com/MagicStack/uvloop'
    depends = ['cython', 'setuptools', 'librt', 'libpthread']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env["LIBUV_CONFIGURE_HOST"] = arch.command_prefix
        env["PLATFORM"] = "android"
        return env


recipe = UvloopRecipe()
