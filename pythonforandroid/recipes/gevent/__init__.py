"""
Note that this recipe doesn't yet build on macOS, the error is:
```
deps/libuv/src/unix/bsd-ifaddrs.c:31:10: fatal error: 'net/if_dl.h' file not found
#include <net/if_dl.h>
         ^~~~~~~~~~~~~
1 error generated.
error: command '/Users/runner/.android/android-ndk/toolchains/llvm/prebuilt/darwin-x86_64/bin/clang' failed with exit code 1
```
"""
import re
from pythonforandroid.logger import info
from pythonforandroid.recipe import PyProjectRecipe


class GeventRecipe(PyProjectRecipe):
    version = '24.11.1'
    url = 'https://github.com/gevent/gevent/archive/refs/tags/{version}.tar.gz'
    depends = ['librt', 'setuptools']
    patches = ["cross_compiling.patch"]

    def get_recipe_env(self, arch, **kwargs):
        """
        - Moves all -I<inc> -D<macro> from CFLAGS to CPPFLAGS environment.
        - Moves all -l<lib> from LDFLAGS to LIBS environment.
        - Copies all -l<lib> from LDLIBS to LIBS environment.
        - Fixes linker name (use cross compiler) and flags (appends LIBS).
        - Feds the command prefix for the configure --host flag.
        """
        env = super().get_recipe_env(arch, **kwargs)
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        regex = re.compile(r'(?:\s|^)-[DI][\S]+')
        env['CPPFLAGS'] = ''.join(re.findall(regex, env['CFLAGS'])).strip()
        env['CFLAGS'] = re.sub(regex, '', env['CFLAGS'])
        info('Moved "{}" from CFLAGS to CPPFLAGS.'.format(env['CPPFLAGS']))
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        regex = re.compile(r'(?:\s|^)-l[\w\.]+')
        env['LIBS'] = ''.join(re.findall(regex, env['LDFLAGS'])).strip()
        env['LIBS'] += ' {}'.format(''.join(re.findall(regex, env['LDLIBS'])).strip())
        env['LDFLAGS'] = re.sub(regex, '', env['LDFLAGS'])
        info('Moved "{}" from LDFLAGS to LIBS.'.format(env['LIBS']))
        # used with the `./configure --host` flag for cross compiling, refs #2805
        env['COMMAND_PREFIX'] = arch.command_prefix
        return env


recipe = GeventRecipe()
