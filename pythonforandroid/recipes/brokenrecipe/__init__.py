from pythonforandroid.toolchain import Recipe


class BrokenRecipe(Recipe):
    def __init__(self):
        print('This is a broken recipe, not a real one!')


recipe = BrokenRecipe()
