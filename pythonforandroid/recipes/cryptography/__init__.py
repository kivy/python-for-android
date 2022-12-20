from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = '3.4.8'
    url = 'https://github.com/pyca/cryptography/archive/{version}.tar.gz'

    # even if rust compilation can be suppressed, setuptools_rust is an
    # install requirement
    depends = ['openssl', 'six', 'setuptools', 'setuptools_rust', 'cffi']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # cryptography version 3.4.8 is the last version supporting suppression
        # of compiling rust extensions, so stick to it for now, since rust
        # cross compilation is a topic on it's own
        env['CRYPTOGRAPHY_DONT_BUILD_RUST'] = '1'

        # suppress default link flags of cryprography. they include -lpthreads
        # which is not available in android NDK, the pthread implementation is
        # inside libc
        env['CRYPTOGRAPHY_SUPPRESS_LINK_FLAGS'] = '1'

        openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        env['CFLAGS'] += openssl_recipe.include_flags(arch)
        env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        env['LIBS'] = openssl_recipe.link_libs_flags()

        return env


recipe = CryptographyRecipe()
