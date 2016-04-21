from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import debug, shprint, info
from os.path import exists, join, dirname
import sh
import glob

class LXMLRecipe(CompiledComponentsPythonRecipe):
    version = '3.6.0'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'
    depends = ['python2', 'libxml2', 'libxslt']
    name = 'lxml'

    call_hostpython_via_targetpython = False # Due to setuptools

    def should_build(self, arch):
        super(LXMLRecipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'liblxml.so'))

    def get_recipe_env(self, arch):
        env = super(LXMLRecipe, self).get_recipe_env(arch)
        bxml = "/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2/"
        bxsl = "/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt"
        targetpython = "%s/include/python2.7/" % dirname(dirname(self.ctx.hostpython))
        env['CC'] += " -I%s/include -I%s -I%s" % (bxml, bxsl, targetpython)
        env['LDSHARED'] = env['CC']
        #env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        # WTH is liblink?
        #env['LDSHARED'] = env['LIBLINK']
        # This linking almost works.  Going to have to muck with LDSHARED to
        # include the libs_collection folder
        #zgoldberg@badass:~/.local/share/python-for-android/build/other_builds/lxml/armeabi/lxml (master)$ /usr/bin/ccache arm-linux-androideabi-ld -L/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2//include -L/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt -L/home/zgoldberg/android-sdks/ndk-bundle/platforms/android-16/arch-arm/usr/lib/ -L/home/zgoldberg/android-sdks/ndk-bundle/platforms/android-16/arch-arm/usr/lib/ -L/home/zgoldberg/.local/share/python-for-android/build/libs_collections/peggo-python/armeabi build/temp.linux-x86_64-2.7/src/lxml/lxml.objectify.o -lxslt -lxml2 -lpython2.7 -lz -lm -o build/lib.linux-x86_64-2.7/lxml/objectify.soi

        return env

recipe = LXMLRecipe()
