from pythonforandroid.toolchain import Recipe


class FFPyPlayerCodecsRecipe(Recipe):
    depends = ['libshine', 'libx264']

    def build_arch(self, arch):
        pass


recipe = FFPyPlayerCodecsRecipe()
