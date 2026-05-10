from pythonforandroid.recipe import PyProjectRecipe, Recipe


class GrpcioRecipe(PyProjectRecipe):
    version = '1.64.0'
    url = 'https://files.pythonhosted.org/packages/source/g/grpcio/grpcio-{version}.tar.gz'
    depends = ["setuptools", "librt", "libpthread"]
    patches = [
        "comment-getserverbyport-r-args.patch",
        "remove-android-log-write.patch",
        "use-ndk-zlib-and-openssl-recipe-include.patch"
    ]

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["NDKPLATFORM"] = "NOTNONE"
        env["GRPC_PYTHON_BUILD_SYSTEM_OPENSSL"] = "1"
        env["GRPC_PYTHON_BUILD_SYSTEM_ZLIB"] = "1"
        env["ZLIB_INCLUDE"] = self.ctx.ndk.sysroot_include_dir
        # replace -I with a space
        openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        env["SSL_INCLUDE"] = openssl_recipe.include_flags(arch).strip().replace("-I", "")
        env["CFLAGS"] += " -U__ANDROID_API__"
        env["CFLAGS"] += " -D__ANDROID_API__={}".format(self.ctx.ndk_api)
        # turn off c++11 warning error of "invalid suffix on literal"
        env["CFLAGS"] += " -Wno-reserved-user-defined-literal"
        env["PLATFORM"] = "android"
        env["LDFLAGS"] += " -llog -landroid"
        env["LDFLAGS"] += openssl_recipe.link_flags(arch)
        return env


recipe = GrpcioRecipe()
