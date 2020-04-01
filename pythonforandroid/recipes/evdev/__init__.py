from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class EvdevRecipe(CompiledComponentsPythonRecipe):
    name = 'evdev'
    version = 'v0.4.7'
    url = 'https://github.com/gvalkov/python-evdev/archive/{version}.zip'

    depends = []

    build_cmd = 'build'

    patches = ['evcnt.patch',
               'keycnt.patch',
               'remove-uinput.patch',
               'include-dir.patch',
               'evdev-permissions.patch']

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['NDKPLATFORM'] = self.ctx.ndk_platform
        return env


recipe = EvdevRecipe()
