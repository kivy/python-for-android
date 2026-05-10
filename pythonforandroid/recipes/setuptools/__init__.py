from pythonforandroid.recipe import PyProjectRecipe


class SetuptoolsRecipe(PyProjectRecipe):
    hostpython_prerequisites = ['setuptools']


recipe = SetuptoolsRecipe()
