from pythonforandroid.recipe import PythonRecipe


class PySDL2Recipe(PythonRecipe):
    version = '0.9.6'
    url = 'https://files.pythonhosted.org/packages/source/P/PySDL2/PySDL2-{version}.tar.gz'

    depends = ['sdl2']


recipe = PySDL2Recipe()
