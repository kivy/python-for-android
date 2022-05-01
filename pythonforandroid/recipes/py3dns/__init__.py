from pythonforandroid.recipe import PythonRecipe


class Py3DNSRecipe(PythonRecipe):
    site_packages_name = 'DNS'
    version = '3.2.1'
    url = 'https://launchpad.net/py3dns/trunk/{version}/+download/py3dns-{version}.tar.gz'
    depends = ['setuptools']
    patches = ['patches/android.patch']
    call_hostpython_via_targetpython = False


recipe = Py3DNSRecipe()
