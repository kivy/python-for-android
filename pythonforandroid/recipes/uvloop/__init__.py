from pythonforandroid.recipe import PyProjectRecipe


class UvloopRecipe(PyProjectRecipe):
    version = 'v0.19.0'
    url = 'git+https://github.com/MagicStack/uvloop'
    depends = ['librt', 'libpthread']

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["LIBUV_CONFIGURE_HOST"] = arch.command_prefix
        env["PLATFORM"] = "android"
        return env


recipe = UvloopRecipe()
