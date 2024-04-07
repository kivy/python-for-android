from pythonforandroid.recipe import RustCompiledComponentsRecipe


class PydanticcoreRecipe(RustCompiledComponentsRecipe):
    version = "2.16.1"
    url = "https://github.com/pydantic/pydantic-core/archive/refs/tags/v{version}.tar.gz"
    site_packages_name = "pydantic_core"


recipe = PydanticcoreRecipe()
