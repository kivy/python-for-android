import re
import os
import sh
from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import CythonRecipe


class GeventRecipe(CythonRecipe):
    version = '1.3.7'
    url = 'https://pypi.python.org/packages/source/g/gevent/gevent-{version}.tar.gz'
    depends = ['greenlet']
    patches = ["cross_compiling.patch"]

    def build_cython_components(self, arch):
        """
        Hack to make it link properly to librt, inserted automatically by the
        installer (Note: the librt doesn't exist in android but it is
        integrated into libc, so we create a symbolic link which we will
        remove when our build finishes)
        """
        link_c = os.path.join(self.ctx.ndk_platform, 'usr', 'lib', 'libc')
        link_rt = os.path.join(self.ctx.ndk_platform, 'usr', 'lib', 'librt')
        shprint(sh.ln, '-sf', link_c + '.so', link_rt + '.so')
        shprint(sh.ln, '-sf', link_c + '.a', link_rt + '.a')
        super(GeventRecipe, self).build_cython_components(arch)
        shprint(sh.rm, link_rt + '.so')
        shprint(sh.rm, link_rt + '.a')

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        """
        - Moves all -I<inc> -D<macro> from CFLAGS to CPPFLAGS environment.
        - Moves all -l<lib> from LDFLAGS to LIBS environment.
        - Fixes linker name (use cross compiler)  and flags (appends LIBS)
        """
        env = super(GeventRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        regex = re.compile(r'(?:\s|^)-[DI][\S]+')
        env['CPPFLAGS'] = ''.join(re.findall(regex, env['CFLAGS'])).strip()
        env['CFLAGS'] = re.sub(regex, '', env['CFLAGS'])
        info('Moved "{}" from CFLAGS to CPPFLAGS.'.format(env['CPPFLAGS']))
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        regex = re.compile(r'(?:\s|^)-l[\w\.]+')
        env['LIBS'] = ''.join(re.findall(regex, env['LDFLAGS'])).strip()
        env['LDFLAGS'] = re.sub(regex, '', env['LDFLAGS'])
        info('Moved "{}" from LDFLAGS to LIBS.'.format(env['LIBS']))
        return env


recipe = GeventRecipe()
