from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class KiwiSolverRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'kiwisolver'
    # Pin to commit `docs: attempt to fix doc building`, the latest one
    # at the time of writing, just to be sure that we have te most up to date
    # version, but it should be pinned to an official release once the c++
    # changes that we want to include are merged to master branch
    #   Note: the commit we want to include is
    #         `Cppy use update and c++11 compatibility` (4858730)
    version = '0846189'
    url = 'https://github.com/nucleic/kiwi/archive/{version}.zip'
    depends = ['cppy']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        if self.need_stl_shared:
            # kiwisolver compile flags does not honor the standard flags:
            # `CPPFLAGS` and `LDLIBS`, so we put in `CFLAGS` and `LDFLAGS` to
            # correctly link with the `c++_shared` library
            env['CFLAGS'] += f' -I{self.ctx.ndk.libcxx_include_dir}'
            env['CFLAGS'] += ' -frtti -fexceptions'

            env['LDFLAGS'] += f' -L{arch.ndk_lib_dir}'
            env['LDFLAGS'] += f' -l{self.stl_lib_name}'
        return env


recipe = KiwiSolverRecipe()
