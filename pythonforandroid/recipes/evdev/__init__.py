from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class EvdevRecipe(CompiledComponentsPythonRecipe):
    name = 'evdev'
    version = 'v0.4.7'
    url = 'https://github.com/gvalkov/python-evdev/archive/{version}.zip'
    call_hostpython_via_targetpython = False

    depends = []

    build_cmd = 'build'

    patches = ['evcnt.patch',
               'keycnt.patch',
               'remove-uinput.patch',
               'include-dir.patch',
               'evdev-permissions.patch']

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['SYSROOT'] = self.ctx.ndk.sysroot
        return env


recipe = EvdevRecipe()
