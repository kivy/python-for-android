from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh

class Libxml2Recipe(Recipe):
    version = '2.7.8'
    url = 'http://xmlsoft.org/sources/libxml2-{version}.tar.gz'
    depends = []
    patches = ['add-glob.c.patch']

    def should_build(self, arch):
        super(Libxml2Recipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libxml2.a'))

    def build_arch(self, arch):
        super(Libxml2Recipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # First we need to build glob.c because its not avail
            # in android ndk


            shprint(sh.Command(env['CC'].split(" ")[0]), env['CC'].split(" ")[1], "-c", "-I.", "glob.c")
            shprint(sh.Command("chmod"), "+x", "glob.o")

            env['LIBS'] = "./glob.o"

            # If the build is done with /bin/sh things blow up,
            # try really hard to use bash
            sed = sh.Command('sed')
            shprint(sh.Command('./configure'),  '--host=arm-linux-eabi',
                    '--without-modules',  '--without-legacy', '--without-hfinistory',  '--without-debug',  '--without-docbook', '--without-python', '--without-threads', '--without-iconv',
                    _env=env)
            shprint(sh.make, _env=env)
            shutil.copyfile('.libs/libxml2.a', join(self.ctx.get_libs_dir(arch.arch), 'libxml2.a'))


    def get_recipe_env(self, arch):
        env = super(Libxml2Recipe, self).get_recipe_env(arch)
        env['CONFIG_SHELL'] = '/bin/bash'
        env['SHELL'] = '/bin/bash'
        env['CC'] = '/usr/bin/ccache arm-linux-androideabi-gcc -DANDROID -mandroid -fomit-frame-pointer'
        env['CCC'] = '/usr/bin/ccache arm-linux-androideabi-g++ -DANDROID -mandroid -fomit-frame-pointer'
        #--sysroot /opt/android-sdks/ndk-bundle/platforms/android-16/arch-arm -I/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxml2/armeabi/libxml2//include -I/home/zgoldberg/.local/share/python-for-android/build/other_builds/libxslt/armeabi/libxslt -I/home/zgoldberg/.local/share/python-for-android/build/python-installs/peggo-python/include/python2.7

        return env

recipe = Libxml2Recipe()
