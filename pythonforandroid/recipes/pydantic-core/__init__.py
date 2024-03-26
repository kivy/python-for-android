from pythonforandroid.recipe import RustCompiledComponentsRecipe
from pythonforandroid.logger import info


class PydanticcoreRecipe(RustCompiledComponentsRecipe):
    version = "2.16.1"
    url = "https://github.com/pydantic/pydantic-core/archive/refs/tags/v{version}.tar.gz"
    use_maturin = True
    hostpython_prerequisites = ["typing_extensions"]

    def should_build(self, arch):
        name = self.folder_name
        if self.ctx.has_package(name.replace("-", "_"), arch):
            info('Python package already exists in site-packages')
            return False
        info('{} apparently isn\'t already in site-packages'.format(name))
        return True


recipe = PydanticcoreRecipe()
