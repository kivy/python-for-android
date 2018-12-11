from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class NetifacesRecipe(CompiledComponentsPythonRecipe):

    version = '0.10.7'

    url = 'https://files.pythonhosted.org/packages/81/39/4e9a026265ba944ddf1fea176dbb29e0fe50c43717ba4fcf3646d099fe38/netifaces-{version}.tar.gz'

    depends = ['setuptools']

    patches = ['fix-build.patch']

    site_packages_name = 'netifaces'

    call_hostpython_via_targetpython = False


recipe = NetifacesRecipe()
