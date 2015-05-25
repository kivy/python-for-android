from toolchain import NDKRecipe, shprint, current_directory
import sh



class LibSDL2Recipe(NDKRecipe):
    # version = "2.0.3"
    # url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"

    def build_arch(self, arch):
        # shprint(sh.xcodebuild,
        #         "ONLY_ACTIVE_ARCH=NO",
        #         "ARCHS={}".format(arch.arch),
        #         "-sdk", arch.sdk,
        #         "-project", "Xcode-iOS/SDL/SDL.xcodeproj",
        #         "-target", "libSDL",
        #         "-configuration", "Release")
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = LibSDL2Recipe()

