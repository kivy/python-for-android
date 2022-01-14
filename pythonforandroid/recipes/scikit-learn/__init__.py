from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe
from multiprocessing import cpu_count


class ThisRecipe(CompiledComponentsPythonRecipe):

    site_packages_name = 'scikit-learn'
    version = '0.23.2'
    url = f'https://github.com/{site_packages_name}/{site_packages_name}/archive/{version}.zip'
    depends = ['setuptools', 'scipy', 'joblib', 'threadpoolctl']
    call_hostpython_via_targetpython = False
    need_stl_shared = True
    patches = ['cross-compile.patch']

    def build_compiled_components(self, arch):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().build_compiled_components(arch)
        self.setup_extra_args = []

    def rebuild_compiled_components(self, arch, env):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().rebuild_compiled_components(arch, env)
        self.setup_extra_args = []

    def strip_ccache(self, env):
        for key, value in env.items():
            parts = value.split(' ')
            if 'ccache' in parts[0]:
                env[key] = ' '.join(parts[1:])

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        self.strip_ccache(env)
        scipy_build_dir = Recipe.get_recipe('scipy', self.ctx).get_build_dir(arch.arch)
        env['PYTHONPATH'] += f':{scipy_build_dir}'
        env['CXX'] += f' -Wl,-l{self.stl_lib_name}'
        return env


recipe = ThisRecipe()
