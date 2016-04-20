from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh

class LXMLRecipe(Recipe):
    version = '3.6.0'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'
    depends = ['python2', 'libxml2', 'libxslt']

    def should_build(self, arch):
        super(LXMLRecipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'liblxml.so'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    "-p%s" % arch.arch,
                    "-I/home/zgoldberg/.local/share/python-for-android/dists/peggo-python/python-install/include/python2.7/pyconfig.h",
                    "-I/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2/include",
                    "-I/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt"

            , _env=env)

        super(LXMLRecipe, self).build_arch(arch)

    def get_recipe_env(self, arch):
        env = super(LXMLRecipe, self).get_recipe_env(arch)
        bxml = "/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2/"
        bxsl = "/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt"
        env['CC'] += " -I%s/include -I%s" % (bxml, bxsl)
        env['LDFLAGS'] = (" -L%s/libxslt/.libs -L%s/libexslt/.libs -L%s/.libs -L%s/libxslt -L%s/libexslt -L%s/ " % (bxsl, bxsl, bxml, bxsl, bxsl, bxml)) + env['LDFLAGS']
        env['LDSHARED'] = "$LIBLINK"
        env['PATH'] += ":%s" % bxsl
        env['CFLAGS'] += ' -Os'
        return env

recipe = LXMLRecipe()
