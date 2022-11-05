"""Build AIOHTTP"""
from typing import List
from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class AIOHTTPRecipe(CppCompiledComponentsPythonRecipe):  # type: ignore # pylint: disable=R0903
    version = "3.8.3"
    url = "https://pypi.python.org/packages/source/a/aiohttp/aiohttp-{version}.tar.gz"
    name = "aiohttp"
    depends: List[str] = ["setuptools"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['LDFLAGS'] += ' -lc++_shared'
        return env


recipe = AIOHTTPRecipe()
