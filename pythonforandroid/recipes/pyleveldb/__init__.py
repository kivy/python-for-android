from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class PyLevelDBRecipe(CppCompiledComponentsPythonRecipe):
    version = '0.194'
    url = ('https://pypi.python.org/packages/source/l/leveldb/'
           'leveldb-{version}.tar.gz')
    depends = ['snappy', 'leveldb', 'setuptools']
    patches = ['bindings-only.patch']
    site_packages_name = 'leveldb'

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        snappy_recipe = self.get_recipe('snappy', self.ctx)
        leveldb_recipe = self.get_recipe('leveldb', self.ctx)

        env["LDFLAGS"] += " -L" + snappy_recipe.get_build_dir(arch.arch)
        env["LDFLAGS"] += " -L" + leveldb_recipe.get_build_dir(arch.arch)

        env["SNAPPY_BUILD_PATH"] = snappy_recipe.get_build_dir(arch.arch)
        env["LEVELDB_BUILD_PATH"] = leveldb_recipe.get_build_dir(arch.arch)

        return env


recipe = PyLevelDBRecipe()
