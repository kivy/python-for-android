from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class NetifacesRecipe(CompiledComponentsPythonRecipe):

    version = '0.10.9'

    url = 'https://files.pythonhosted.org/packages/source/n/netifaces/netifaces-{version}.tar.gz'

    depends = ['setuptools']

    patches = ['fix-build.patch']

    site_packages_name = 'netifaces'

    call_hostpython_via_targetpython = False


recipe = NetifacesRecipe()
