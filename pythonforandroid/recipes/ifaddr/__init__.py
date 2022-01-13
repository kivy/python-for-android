from pythonforandroid.recipe import PythonRecipe


class IfaddrRecipe(PythonRecipe):
    name = 'ifaddr'
    version = '0.1.7'
    url = 'https://pypi.python.org/packages/source/i/ifaddr/ifaddr-{version}.tar.gz'
    depends = ['setuptools', 'ifaddrs', 'ipaddress;python_version<"3.3"']
    call_hostpython_via_targetpython = False
    patches = ["getifaddrs.patch"]


recipe = IfaddrRecipe()
