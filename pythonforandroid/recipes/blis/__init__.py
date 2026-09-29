from pythonforandroid.archs import Archx86_64
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class BlisRecipe(CompiledComponentsPythonRecipe):
    version = "1.2.1"
    url = "https://github.com/explosion/cython-blis/archive/refs/tags/release-v{version}.tar.gz"
    depends = [
        "setuptools",
        "cython",
    ]
    hostpython_prerequisites = [  # build only
        "numpy",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def get_recipe_env(self, arch=None, with_flags_in_cc=False):
        env = super().get_recipe_env(arch, with_flags_in_cc)

        # see https://github.com/flame/blis/blob/master/config_registry
        # if isinstance(arch, ArchAarch_64):
        #     env["BLIS_ARCH"] = "arm64"
        if isinstance(arch, Archx86_64):
            env["BLIS_ARCH"] = "x86_64"
        else:
            env["BLIS_ARCH"] = "generic"

        if "CC" in env:
            cli = env["CC"].split()[0]
            ccache_bin = cli if "ccache" in cli else ""

            env["BLIS_COMPILER"] = " ".join(
                [
                    ccache_bin,
                    arch.get_clang_exe(with_target=True),
                ]
            )

        return env

    def get_hostrecipe_env(self, arch):
        env = super().get_hostrecipe_env(arch)
        # see https://github.com/explosion/cython-blis/blob/bdb10be0698002e1d93f79cd91fc1a38f0da3fb3/setup.py#L290
        env["BLIS_COMPILER"] = "/usr/bin/ccache gcc"

        return env


recipe = BlisRecipe()
