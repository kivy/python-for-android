from pythonforandroid.recipe import PythonRecipe


class Enum34Recipe(PythonRecipe):
    version = '1.1.6'
    url = 'https://pypi.python.org/packages/source/e/enum34/enum34-{version}.tar.gz'
    depends = ['setuptools']
    site_packages_name = 'enum'
    call_hostpython_via_targetpython = False

    def should_build(self, arch):
        if 'python3' in self.ctx.python_recipe.name:
            # Since python 3.6 the enum34 library is no longer compatible with
            # the standard library and it will cause errors, so we disable it
            # in favour of the internal module, but we still add python3 to
            # attribute `depends` because otherwise we will not be able to
            # build the cryptography recipe.
            return False
        return super(Enum34Recipe, self).should_build(arch)


recipe = Enum34Recipe()
