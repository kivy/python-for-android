from toolchain import NDKRecipe, shprint, current_directory, info_main
from os.path import exists
import sh



class LibSDL2Recipe(NDKRecipe):
    version = "2.0.3"
    url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"

    def prebuild_arch(self, arch):
        with current_directory(self.get_build_container_dir(arch)):
            if exists('SDL2-{}'.format(self.version)):
                if not exists('SDL'):
                    shprint(sh.mv, 'SDL2-{}'.format(self.version), 'SDL')
                else:
                    shprint(sh.rm, '-rf', 'SDL2-{}'.format(self.version))

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

