from pythonforandroid.recipe import PythonRecipe


class CoverageRecipe(PythonRecipe):

    version = '4.1'

    url = 'https://pypi.python.org/packages/2d/10/6136c8e10644c16906edf4d9f7c782c0f2e7ed47ff2f41f067384e432088/coverage-{version}.tar.gz'

    depends = ['hostpython3', 'setuptools']

    patches = ['fallback-utf8.patch']

    site_packages_name = 'coverage'

    call_hostpython_via_targetpython = False


recipe = CoverageRecipe()
