from pythonforandroid.toolchain import Recipe, current_directory, shprint
import sh
import os.path


class LibpqRecipe(Recipe):
    version = '9.5.3'
    url = 'http://ftp.postgresql.org/pub/source/v{version}/postgresql-{version}.tar.bz2'
    depends = [('python2', 'python3crystax')]

    def should_build(self, arch):
        return not os.path.isfile('{}/libpq.a'.format(self.ctx.get_libs_dir(arch.arch)))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--without-readline', '--host=arm-linux',
                    _env=env)
            shprint(sh.make, 'submake-libpq', _env=env)
            shprint(sh.cp, '-a', 'src/interfaces/libpq/libpq.a',
                    self.ctx.get_libs_dir(arch.arch))

recipe = LibpqRecipe()
