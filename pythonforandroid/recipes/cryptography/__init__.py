from pythonforandroid.recipe import RustCompiledComponentsRecipe
from os.path import join


class CryptographyRecipe(RustCompiledComponentsRecipe):

    name = 'cryptography'
    version = '42.0.1'
    url = 'https://github.com/pyca/cryptography/archive/refs/tags/{version}.tar.gz'
    depends = ['openssl', 'six', 'setuptools', 'cffi']
    # recipe built cffi does not work on apple M1
    hostpython_prerequisites = ["semantic_version", "cffi"]

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        openssl_build_dir = self.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        build_target = self.RUST_ARCH_CODES[arch.arch].upper().replace("-", "_")
        openssl_include = "{}_OPENSSL_INCLUDE_DIR".format(build_target)
        openssl_libs = "{}_OPENSSL_LIB_DIR".format(build_target)
        env[openssl_include] = join(openssl_build_dir, 'include')
        env[openssl_libs] = join(openssl_build_dir)
        return env


recipe = CryptographyRecipe()
