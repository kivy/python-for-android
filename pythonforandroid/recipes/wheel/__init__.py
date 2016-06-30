
from pythonforandroid.toolchain import PythonRecipe


class WheelRecipe(PythonRecipe):
    version = '0.29.0'
    url = 'https://pypi.python.org/packages/source/w/wheel/wheel-{version}.tar.gz'

    depends = [('python2', 'python3crystax')]

    call_hostpython_via_targetpython = False
    install_in_targetpython = False
    install_in_hostpython = True


recipe = WheelRecipe()
