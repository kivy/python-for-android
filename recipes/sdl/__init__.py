from toolchain import NDKRecipe, shprint
import sh



class LibSDLRecipe(NDKRecipe):
    version = "1.2.14"
    url = None  
    name = 'sdl'
    depends = ['python2']

    def prebuild_armeabi(self):
        print('Debug: sdl recipe dir is ' + self.get_build_dir())

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


recipe = LibSDLRecipe()

