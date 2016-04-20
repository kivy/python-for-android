from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import debug, shprint, info
from os.path import exists, join
import sh
import glob

class LXMLRecipe(Recipe):
    version = '3.6.0'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'
    depends = ['python2', 'libxml2', 'libxslt']
    name = 'lxml'

    def should_build(self, arch):
        super(LXMLRecipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'liblxml.so'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/png -I{jni_path}/jpeg'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl/include -I{jni_path}/sdl_mixer'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl_ttf -I{jni_path}/sdl_image'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        debug('pygame cflags', env['CFLAGS'])


        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{libs_path} -L{src_path}/obj/local/{arch} -lm -lz'.format(
            libs_path=self.ctx.libs_dir, src_path=self.ctx.bootstrap.build_dir, arch=env['ARCH'])

        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')

        with current_directory(self.get_build_dir(arch.arch)):
            info('hostpython is ' + self.ctx.hostpython)
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, 'setup.py',
                    'build_ext',
                    "-I/home/zgoldberg/.local/share/python-for-android/dists/peggo-python/python-install/include/python2.7/pyconfig.h",
                    "-I/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2/include",
                    "-I/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt",
                    _tail=10000, _critical=True, _env=env)

            build_lib = glob.glob('./build/lib*')
            assert len(build_lib) == 1

            shprint(sh.find, ".", '-iname', '*.pyx', '-exec',
                    env['CYTHON'], '{}', ';')

            shprint(hostpython, 'setup.py',
                    'build_ext', "-v",
                    _tail=10000, _critical=True, _env=env)

            shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                    env['STRIP'], '{}', ';')

            shprint(hostpython, 'setup.py',
                    'install', "-O2",
                    _tail=10000, _critical=True, _env=env)

            #env['PYTHONPATH'] += $BUILD_hostpython/Lib/site-packages
            #try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages



        super(LXMLRecipe, self).build_arch(arch)

    def get_recipe_env(self, arch):
        env = super(LXMLRecipe, self).get_recipe_env(arch)
        bxml = "/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2/"
        bxsl = "/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt"
        env['CC'] += " -I%s/include -I%s" % (bxml, bxsl)
        env['LDFLAGS'] = (" -L%s/libxslt/.libs  -L%s/.libs -L%s/libxslt -L%s/ " % (bxsl, bxsl, bxml, bxsl)) + env['LDFLAGS']
        env['CYTHON'] = "cython"
        env['LDSHARED'] = "$LIBLINK"
        env['PATH'] += ":%s" % bxsl
        env['CFLAGS'] += ' -Os'
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform

        # Every recipe uses its own liblink path, object files are collected and biglinked later
        liblink_path = join(self.get_build_container_dir(arch.arch), 'objects_{}'.format(self.name))
        env['LIBLINK_PATH'] = liblink_path
        ensure_dir(liblink_path)
        return env

recipe = LXMLRecipe()
