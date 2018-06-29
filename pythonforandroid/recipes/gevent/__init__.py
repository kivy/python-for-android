import re
from pythonforandroid.logger import info
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class GeventRecipe(CompiledComponentsPythonRecipe):
    version = '1.1.1'
    url = 'https://pypi.python.org/packages/source/g/gevent/gevent-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'greenlet']
    patches = ["gevent.patch"]
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        """
        - Moves all -I<inc> -D<macro> from CFLAGS to CPPFLAGS environment.
        - Moves all -l<lib> from LDFLAGS to LIBS environment.
        - Fixes linker name (use cross compiler)  and flags (appends LIBS)
        """
        env = super(GeventRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        regex = re.compile('\s*-[DI][\S]+')
        env['CPPFLAGS'] = ''.join(re.findall(regex, env['CFLAGS'])).strip()
        env['CFLAGS'] = re.sub(regex, '', env['CFLAGS'])
        info('Moved "{}" from CFLAGS to CPPFLAGS.'.format(env['CPPFLAGS']))
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        regex = re.compile('\s*-l[\w\.]+')
        env['LIBS'] = ''.join(re.findall(regex, env['LDFLAGS'])).strip()
        env['LDFLAGS'] = re.sub(regex, '', env['LDFLAGS'])
        info('Moved "{}" from LDFLAGS to LIBS.'.format(env['LIBS']))
        # linker to use the correct gcc (cross compiler) plus additional libs
        env['LDSHARED'] = '{} -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions {}'.format(env['CC'], env['LIBS'])
        return env


recipe = GeventRecipe()
