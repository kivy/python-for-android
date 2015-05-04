
from toolchain import Recipe, shprint
import sh

class Python2Recipe(Recipe):
    version = "2.7.2"
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'python2'

    # python2 depends not enabled yet
    #depends = ['hostpython2']  

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
