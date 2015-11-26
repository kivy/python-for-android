from pythonforandroid.toolchain import Recipe

class BrokenRecipe(Recipe):
    info = 'This is a broken recipe, not a real one!'

recipe = BrokenRecipe()
