import os
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class GeventRecipe(CompiledComponentsPythonRecipe):
    version = '1.1.1'
    url = 'https://pypi.python.org/packages/source/g/gevent/gevent-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'greenlet']
    patches = ["gevent.patch"]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(GeventRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # sets linker to use the correct gcc (cross compiler)
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        env['CPPFLAGS'] = env['CFLAGS'] + ' -I{}/sources/python/3.5/include/python/'.format(self.ctx.ndk_dir)
        env['CFLAGS'] = ''
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        env['LDFLAGS'] = env['LDFLAGS'].replace('-lm', '').replace('-lcrystax', '')
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        env['LIBS'] = ' -lm'
        if self.ctx.ndk == 'crystax':
            env['LIBS'] += ' -lcrystax -lpython{}m'.format(self.ctx.python_recipe.version[0:3])
        env['LDSHARED'] += env['LIBS']
        return env


recipe = GeventRecipe()
