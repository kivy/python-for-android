from typing import Any

from pythonforandroid.archs import Arch
from pythonforandroid.recipe import PyProjectRecipe


class MsgspecRecipe(PyProjectRecipe):
    url = 'https://github.com/jcrist/msgspec/archive/refs/tags/{version}.tar.gz'
    depends = ['python3', 'setuptools']
    site_packages_name = 'msgspec'
    name = 'msgspec'
    version = '0.21.1'

    def get_recipe_env(self, arch: Arch, **kwargs) -> dict[str, Any]:
        env: dict[str, Any] = super().get_recipe_env(arch, **kwargs)
        env['SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MSGSPEC'] = self.version

        return env


recipe = MsgspecRecipe()
