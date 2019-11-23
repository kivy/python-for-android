from pythonforandroid.toolchain import Recipe


class FFPyPlayerCodecsRecipe(Recipe):
    depends = ['libx264']
    # disabled libshine due a missing symbol error (see ffmpeg recipe)

    def build_arch(self, arch):
        pass


recipe = FFPyPlayerCodecsRecipe()
