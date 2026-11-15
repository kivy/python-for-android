from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class PyZintRecipe(CompiledComponentsPythonRecipe):
    version = '0.1.8'
    url = 'https://files.pythonhosted.org/packages/bc/49/ff6ef23a049e9c6a3b447b9bf4dc366a5bd7aca23e950a690e8d2caaaf03/pyzint-{version}.tar.gz#sha256=097680466997af0145b65391f012ba5a73f3b041a4ca27378633ead2d5922ad2'
    md5sum = '3db52703b84f0b3b47d403f05d71a080'
    blake2bsum = '02f231384bd3eaea30c68f9885946d8be5c0dcdd3ffa24790966756c110499fdc5644e90343bc24b7315cff39b477ba7b566038f0707a8c84cdf201f2307d3e0'

    depends = ['setuptools']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['CPPFLAGS'] = env.get('CPPFLAGS', '') + ' -include stdint.h'
        return env


recipe = PyZintRecipe()
