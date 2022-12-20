from pythonforandroid.recipe import PythonRecipe


class TypingExtensionsRecipe(PythonRecipe):
    version = '3.10.0.2'
    url = 'https://pypi.python.org/packages/source/t/typing-extensions/typing_extensions-{version}.tar.gz'
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = TypingExtensionsRecipe()
