from pythonforandroid.recipe import RustCompiledComponentsRecipe


class PydanticcoreRecipe(RustCompiledComponentsRecipe):
    version = "2.16.1"
    url = "https://github.com/pydantic/pydantic-core/archive/refs/tags/v{version}.tar.gz"
    use_maturin = True
    hostpython_prerequisites = ["typing_extensions"]
    site_packages_name = "pydantic_core"


recipe = PydanticcoreRecipe()
