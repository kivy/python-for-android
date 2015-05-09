
from toolchain import Recipe, shprint
from os.path import exists, join
from os import uname
import sh

class Python2Recipe(Recipe):
    version = "2.7.2"
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'python2'

    depends = ['hostpython2']  

    def prebuild_armeabi(self):
        build_dir = self.get_build_dir('armeabi')
        if exists(join(build_dir, '.patched')):
            print('Python2 already patched, skipping.')
            return
        self.apply_patch(join('patches', 'Python-{}-xcompile.patch'.format(self.version)))
	self.apply_patch(join('patches', 'disable-modules.patch'))
	self.apply_patch(join('patches', 'fix-locale.patch'))
	self.apply_patch(join('patches', 'fix-gethostbyaddr.patch'))
	self.apply_patch(join('patches', 'fix-setup-flags.patch'))
	self.apply_patch(join('patches', 'fix-filesystemdefaultencoding.patch'))
	self.apply_patch(join('patches', 'fix-termios.patch'))
	self.apply_patch(join('patches', 'custom-loader.patch'))
	self.apply_patch(join('patches', 'verbose-compilation.patch'))
	self.apply_patch(join('patches', 'fix-remove-corefoundation.patch'))
	self.apply_patch(join('patches', 'fix-dynamic-lookup.patch'))
	self.apply_patch(join('patches', 'fix-dlfcn.patch'))

        if uname()[0] == 'Linux':
            self.apply_patch(join('patches', 'fix-configure-darwin.patch'))
            self.apply_patch(join('patches', 'fix-distutils-darwin.patch'))

        shprint(sh.touch, join(build_dir, 'patched'))


    def build_arch(self, arch):
        # shprint(sh.xcodebuild,
        #         "ONLY_ACTIVE_ARCH=NO",
        #         "ARCHS={}".format(arch.arch),
        #         "-sdk", arch.sdk,
        #         "-project", "Xcode-iOS/SDL/SDL.xcodeproj",
        #         "-tarelf.et", "libSDL",
        #         "-configuration", "Release")
        env = self.get_recipe_env(arch)
        shprint(sh.ndk_build,
                "V=1", "sdl2",
                _env=env)


recipe = Python2Recipe()
