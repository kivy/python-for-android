from pythonforandroid.toolchain import Recipe


class FFPyPlayerCodecsRecipe(Recipe):
    depends = ['libx264', 'libshine']

    def build_arch(self, arch):
        pass


recipe = FFPyPlayerCodecsRecipe()
