from os.path import join

from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class PandasRecipe(CppCompiledComponentsPythonRecipe):
    version = '1.0.3'
    url = 'https://github.com/pandas-dev/pandas/releases/download/v{version}/pandas-{version}.tar.gz'  # noqa

    depends = ['cython', 'numpy', 'pytz', 'libbz2', 'liblzma']

    python_depends = ['python-dateutil']
    patches = ['fix_numpy_includes.patch']

    call_hostpython_via_targetpython = False
    need_stl_shared = True

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # we need the includes from our installed numpy at site packages
        # because we need some includes generated at numpy's compile time
        env['NUMPY_INCLUDES'] = join(
            self.ctx.get_python_install_dir(arch.arch), "numpy/core/include",
        )

        # this flag below is to fix a runtime error:
        #   ImportError: dlopen failed: cannot locate symbol
        #   "_ZTVSt12length_error" referenced by
        #   "/data/data/org.test.matplotlib_testapp/files/app/_python_bundle
        #   /site-packages/pandas/_libs/window/aggregations.so"...
        env['LDFLAGS'] += f' -landroid  -l{self.stl_lib_name}'
        return env


recipe = PandasRecipe()
