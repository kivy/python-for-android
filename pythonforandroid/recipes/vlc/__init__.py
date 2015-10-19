from pythonforandroid.toolchain import Recipe, shprint, current_directory, warning, info, debug 
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

    def prebuild_arch(self, arch):
        super(VlcRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        port_dir = join(build_dir, 'vlc-port-android')
        aar_path = join(port_dir, 'libvlc', 'build', 'outputs', 'aar')
        aar = environ.get(self.ENV_LIBVLC_AAR,
                   join(aar_path, 'libvlc-{}.aar'.format(self.version)))
        if not exists(aar):
            if environ.has_key(''):
                warning("Error: libvlc-<ver>.aar bundle not found in {}".format(aar))
                info("check {} environment!".format(self.ENV_LIBVLC_AAR))
                raise Exception("vlc .aar bundle not found by path specified in {}".format(self.ENV_LIBVLC_AAR))
            warning("set path to precompiled libvlc-<ver>.aar bundle in {} environment!".format(self.ENV_LIBVLC_AAR))
            info("libvlc-<ver>.aar for android not found!")
            info("should build from sources at {}".format(port_dir))
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
        aar = environ.get(self.ENV_LIBVLC_AAR,
                   join(aar_path, 'libvlc-{}.aar'.format(self.version)))
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
                try:
                    if not exists(join(port_dir, 'bin', 'VLC-debug.apk')):
                        shprint(sh.Command('./compile.sh'), _env=env)
                    shprint(sh.Command('./compile-libvlc.sh'), _env=env)
                except sh.ErrorReturnCode_1, err:
                    warning("Error: vlc compilation failed")
                    lines = err.stdout.splitlines()
                    N = 20
                    if len(lines) <= N:
                        info('STDOUT:\n{}\t{}{}'.format(Fore.YELLOW, '\t\n'.join(lines), Fore.RESET))
                    else:
                        info('STDOUT (last {} lines of {}):\n{}\t{}{}'.format(N, len(lines), Fore.YELLOW, '\t\n'.join(lines[-N:]), Fore.RESET))
                    lines = err.stderr.splitlines()
                    if len(lines):
                        warning('STDERR:\n{}\t{}{}'.format(Fore.RED, '\t\n'.join(lines), Fore.RESET))
                    raise Exception("vlc compilation failed")
        shprint(sh.cp, '-a', aar, self.ctx.aars_dir)

recipe = VlcRecipe()
