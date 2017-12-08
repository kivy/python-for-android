from pythonforandroid.toolchain import PythonRecipe

class RpdbRecipe(PythonRecipe):
    version = '0.1.6'
    url = 'https://pypi.python.org/packages/53/b7/6663ec9c0157cf7c766bd4c9dca957ca744f0b3b16c945be7e8f8d0b2142/rpdb-0.1.6.tar.gz#md5=1566f936f0f381172ecf918f7a65f882'
    depends = ['python2']
    site_packages_name = 'rpdb'
    call_hostpython_via_targetpython = False

recipe = RpdbRecipe()
