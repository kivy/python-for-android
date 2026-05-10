from pythonforandroid.recipe import PyProjectRecipe


class ApswRecipe(PyProjectRecipe):
    version = '3.50.4.0'
    url = 'https://github.com/rogerbinns/apsw/releases/download/{version}/apsw-{version}.tar.gz'
    depends = ['sqlite3']
    site_packages_name = 'apsw'

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        sqlite_recipe = self.get_recipe('sqlite3', self.ctx)
        env['CFLAGS'] += ' -I' + sqlite_recipe.get_build_dir(arch.arch)
        env['LIBS'] = env.get('LIBS', '') + ' -lsqlite3'
        return env


recipe = ApswRecipe()
