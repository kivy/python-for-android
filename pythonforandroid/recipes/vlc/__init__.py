from pythonforandroid.toolchain import Recipe, current_directory
from pythonforandroid.logger import info, debug, shprint, warning
from os.path import exists, join
from os import environ
import sh
from colorama import Fore, Style

class VlcRecipe(Recipe):
    version = '3.0.0'
    url = None
    name = 'vlc'

    depends = []

    port_git = 'http://git.videolan.org/git/vlc-ports/android.git'
    vlc_git = 'http://git.videolan.org/git/vlc.git'
    ENV_LIBVLC_AAR = 'LIBVLC_AAR'
    aars = {} # for future use of multiple arch

    def prebuild_arch(self, arch):
        super(VlcRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        port_dir = join(build_dir, 'vlc-port-android')
        if self.ENV_LIBVLC_AAR in environ:
            self.aars[arch] = aar = environ.get(self.ENV_LIBVLC_AAR)
            if not exists(aar):
                warning("Error: libvlc-<ver>.aar bundle " \
                           "not found in {}".format(aar))
                info("check {} environment!".format(self.ENV_LIBVLC_AAR))
                exit(1)
        else:
            aar_path = join(port_dir, 'libvlc', 'build', 'outputs', 'aar')
            self.aars[arch] = aar = join(aar_path, 'libvlc-{}.aar'.format(self.version))
            warning("HINT: set path to precompiled libvlc-<ver>.aar bundle " \
                        "in {} environment!".format(self.ENV_LIBVLC_AAR))
            info("libvlc-<ver>.aar should build " \
                        "from sources at {}".format(port_dir))
            if not exists(join(port_dir, 'compile.sh')):
                info("clone vlc port for android sources from {}".format(
                            self.port_git))
                shprint(sh.git, 'clone', self.port_git, port_dir,
                            _tail=20, _critical=True)
            vlc_dir = join(port_dir, 'vlc')
            if not exists(join(vlc_dir, 'Makefile.am')):
                info("clone vlc sources from {}".format(self.vlc_git))
                shprint(sh.git, 'clone', self.vlc_git, vlc_dir,
                            _tail=20, _critical=True)

    def build_arch(self, arch):
        super(VlcRecipe, self).build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        port_dir = join(build_dir, 'vlc-port-android')
        aar = self.aars[arch]
        if not exists(aar):
            with current_directory(port_dir):
                env = dict(environ)
                env.update({
                    'ANDROID_ABI': arch.arch,
                    'ANDROID_NDK': self.ctx.ndk_dir,
                    'ANDROID_SDK': self.ctx.sdk_dir,
                })
                info("compiling vlc from sources")
                debug("environment: {}".format(env))
                if not exists(join('bin', 'VLC-debug.apk')):
                     shprint(sh.Command('./compile.sh'), _env=env,
                                  _tail=50, _critical=True)
                shprint(sh.Command('./compile-libvlc.sh'), _env=env,
                            _tail=50, _critical=True)
        shprint(sh.cp, '-a', aar, self.ctx.aars_dir)

recipe = VlcRecipe()
