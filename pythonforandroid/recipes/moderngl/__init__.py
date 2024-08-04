from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class ModernGLRecipe(CppCompiledComponentsPythonRecipe):
    version = '5.10.0'
    url = 'https://github.com/moderngl/moderngl/archive/refs/tags/{version}.tar.gz'

    site_packages_name = 'moderngl'
    name = 'moderngl'

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['LDFLAGS'] += ' -lstdc++'
        return env


recipe = ModernGLRecipe()
