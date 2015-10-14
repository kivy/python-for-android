from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
from os.path import exists, join, expanduser, basename
from os import environ
import sh
import glob

class VlcRecipe(Recipe):
    version = '3.0.0'
    url = None
    name = 'vlc'

    depends = ['pyjnius', 'android', 'kivy']

    port_git = 'http://git.videolan.org/git/vlc-ports/android.git'
    vlc_git = 'http://git.videolan.org/git/vlc.git'

    def prebuild_arch(self, arch):
        super(VlcRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        port_dir = join(build_dir, 'vlc-port-android')
        aar_path = join(port_dir, 'libvlc', 'build', 'outputs', 'aar')
        aar = environ.get('LIBVLC_AAR',
                   join(aar_path, 'libvlc-{}.aar'.format(self.version)))
        jar = join(build_dir, 'libvlc.jar')
        if not exists(aar):
            if not environ.has_key('LIBVLC_AAR'):
                warning("set path to ready libvlc-<ver>.aar bundle in LIBVLC_AAR environment!")
            info("libvlc-<ver>.aar for android not found!")
            info("should build sources at {}".format(port_dir))
            if not exists(join(port_dir, 'compile.sh')):
                info("clone vlc port for android sources from {}".format(self.port_git))
                shprint(sh.git, 'clone', self.port_git, port_dir)
            vlc_dir = join(port_dir, 'vlc')
            if not exists(join(vlc_dir, 'Makefile.am')):
                info("clone vlc sources from {}".format(self.vlc_git))
                shprint(sh.git, 'clone', self.vlc_git, vlc_dir)

    def build_arch(self, arch):
        super(VlcRecipe, self).build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        port_dir = join(build_dir, 'vlc-port-android')
        aar_path = join(port_dir, 'libvlc', 'build', 'outputs', 'aar')
        aar = environ.get('LIBVLC_AAR',
                   join(aar_path, 'libvlc-{}.aar'.format(self.version)))
        jar = join(build_dir, 'libvlc.jar')
        if not exists(aar):
            with current_directory(port_dir):
                env = dict(environ)
                env.update({
                    'ANDROID_ABI': arch.arch,
                    'ANDROID_NDK': self.ctx.ndk_dir,
                    'ANDROID_SDK': self.ctx.sdk_dir,
                })
                info("compile vlc from sources")
                info("environment: {}".format(env))
                if not exists(join(port_dir, 'bin', 'VLC-debug.apk')):
                    shprint(sh.Command('./compile.sh'), _env=env)
                shprint(sh.Command('./compile-libvlc.sh'), _env=env)
        shprint(sh.cp, '-a', aar, self.ctx.aars_dir)

recipe = VlcRecipe()
