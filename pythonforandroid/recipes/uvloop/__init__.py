from pythonforandroid.recipe import PyProjectRecipe


class UvloopRecipe(PyProjectRecipe):
    # 0.19.0
    version = '6c770dc3fbdd281d15c2ad46588c139696f9269c'
    url = 'git+https://github.com/MagicStack/uvloop'
    depends = ['librt', 'libpthread']

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["LIBUV_CONFIGURE_HOST"] = arch.command_prefix
        env["PLATFORM"] = "android"
        return env


recipe = UvloopRecipe()
