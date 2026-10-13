from pythonforandroid.recipe import RustCompiledComponentsRecipe
from os.path import join


class CryptographyRecipe(RustCompiledComponentsRecipe):

    name = 'cryptography'
    version = '46.0.3'
    url = 'https://github.com/pyca/cryptography/archive/refs/tags/{version}.tar.gz'
    depends = ['openssl', 'cffi']
    hostpython_prerequisites = ['maturin', 'cffi']
    patches = ['android-cross-include-dir.patch']

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        openssl_build_dir = self.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        build_target = self.RUST_ARCH_CODES[arch.arch].upper().replace("-", "_")
        openssl_include = "{}_OPENSSL_INCLUDE_DIR".format(build_target)
        openssl_libs = "{}_OPENSSL_LIB_DIR".format(build_target)
        env[openssl_include] = join(openssl_build_dir, 'include')
        env[openssl_libs] = join(openssl_build_dir)
        env["ANDROID_API_LEVEL"] = str(self.ctx.ndk_api)
        # cryptography-cffi's build.rs (see android-cross-include-dir.patch)
        # asks the *host* python for its own include_dirs via setuptools,
        # which is wrong when cross-compiling: it returns hostpython3's
        # native Python.h instead of the Android target's, breaking
        # CPython's LONG_BIT sanity check in pyport.h.
        env["P4A_PYTHON_INCLUDE_DIR"] = self.ctx.python_recipe.include_root(arch.arch)
        # Android's bionic linker only resolves symbols from explicitly listed
        # NEEDED libraries.  abi3 extensions don't link against libpython, so
        # _Py_NoneStruct (and other Python symbols) can't be found at dlopen
        # time.  Explicitly link against libpython so Android resolves them.
        python_ver = self.python_major_minor_version
        env["RUSTFLAGS"] = (
            env.get("RUSTFLAGS", "")
            + " -Clink-args=-lpython{}".format(python_ver)
        )
        return env


recipe = CryptographyRecipe()