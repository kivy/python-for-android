from pythonforandroid.recipe import PythonRecipe


class PyusbRecipe(PythonRecipe):
    name = 'pyusb'
    version = '1.0.0b1'
    url = 'https://pypi.python.org/packages/source/p/pyusb/pyusb-{version}.tar.gz'
    depends = []
    site_packages_name = 'usb'

    patches = ['fix-android.patch']


recipe = PyusbRecipe()
