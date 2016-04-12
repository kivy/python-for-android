from pythonforandroid.toolchain import BootstrapNDKRecipe, current_directory
from pythonforandroid.logger import shprint, info
from os.path import exists, join, basename
import sh
import glob

class PygameJNIComponentsRecipe(BootstrapNDKRecipe):
    version = 'master'
    url = 'https://github.com/kivy/p4a-pygame-bootstrap-components/archive/{version}.zip'
    dir_name = 'bootstrap_components'

    def prebuild_arch(self, arch):
        super(PygameJNIComponentsRecipe, self).postbuild_arch(arch)

        info('Unpacking pygame bootstrap JNI dir components')
        with current_directory(self.get_build_container_dir(arch)):
            if exists('sdl'):
                info('sdl dir exists, so it looks like the JNI components' +
                     'are already unpacked. Skipping.')
                return
            for dirn in glob.glob(join(self.get_build_dir(arch),
                                       'pygame_bootstrap_jni', '*')):
                if basename(dirn) not in ['freetype', 'sqlite3']:
                    shprint(sh.mv, dirn, './')
        info('Unpacking was successful, deleting original container dir')
        shprint(sh.rm, '-rf', self.get_build_dir(arch))

    def build_arch(self, arch):
        # TO FORCE BUILD LIBS BEFORE PIL RECIPE
        if 'pil' in self.ctx.recipe_build_order:
            env = self.get_recipe_env(arch)
            with current_directory(self.get_jni_dir()):
                shprint(sh.ndk_build, "V=1", "png", _env=env)
                shprint(sh.ndk_build, "V=1", "jpeg", _env=env)


recipe = PygameJNIComponentsRecipe()
