from toolchain import Recipe, shprint
import sh



class LibSDL2Recipe(Recipe):
    version = "2.0.3"
    url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"
    # version = "iOS-improvements"
    # url = "https://bitbucket.org/slime73/sdl-experiments/get/{version}.tar.gz"
    library = "Xcode-iOS/SDL/build/Release-{arch.sdk}/libSDL2.a"
    include_dir = "include"
    pbx_frameworks = ["OpenGLES", "AudioToolbox", "QuartzCore", "CoreGraphics",
            "CoreMotion"]

    def build_arch(self, arch):
        # shprint(sh.xcodebuild,
        #         "ONLY_ACTIVE_ARCH=NO",
        #         "ARCHS={}".format(arch.arch),
        #         "-sdk", arch.sdk,
        #         "-project", "Xcode-iOS/SDL/SDL.xcodeproj",
        #         "-target", "libSDL",
        #         "-configuration", "Release")
        shprint(sh.ndk_build,
                "V=1", "sdl2")


recipe = LibSDL2Recipe()

