
from pythonforandroid.recipe import PythonRecipe
from os.path import join


class ZopeRecipe(PythonRecipe):
    name = 'zope'
    version = '4.1.3'
    url = 'https://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'

    depends = []

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # These are in the old zope recipe but seem like they shouldn't actually be necessary
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        return env

    def postbuild_arch(self, arch):
        super().postbuild_arch(arch)

        # Should do some deleting here


recipe = ZopeRecipe()

# FIXME: @mirko liblink & LD
