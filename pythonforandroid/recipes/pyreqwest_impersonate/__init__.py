from pythonforandroid.logger import info
from pythonforandroid.recipe import RustCompiledComponentsRecipe


class Pyreqwest_impersonateRecipe(RustCompiledComponentsRecipe):
    version = "v0.4.5"
    url = "https://github.com/deedy5/pyreqwest_impersonate/archive/refs/tags/{version}.tar.gz"

    def get_recipe_env_post(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["ANDROID_NDK_HOME"] = self.ctx.ndk.llvm_prebuilt_dir
        return env

    def get_recipe_env_pre(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["ANDROID_NDK_HOME"] = self.ctx.ndk_dir
        return env

    def build_arch(self, arch):
        # Why need of two env?
        # Because there are two dependencies which accepts
        # different ANDROID_NDK_HOME
        self.get_recipe_env = self.get_recipe_env_pre
        prebuild_ = super().build_arch
        try:
            prebuild_(arch)
        except Exception:
            info("pyreqwest_impersonate first build failed, as expected")
            self.get_recipe_env = self.get_recipe_env_post
            prebuild_(arch)


recipe = Pyreqwest_impersonateRecipe()
