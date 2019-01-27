from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint, info
from os.path import exists, join
import sh
import glob


class PygameJNIComponentsRecipe(BootstrapNDKRecipe):
    version = 'master'
    url = 'https://github.com/kivy/p4a-pygame-bootstrap-components/archive/{version}.zip'
    dir_name = 'bootstrap_components'
    patches = ['jpeg-ndk15-plus.patch']

    def prebuild_arch(self, arch):
        super(PygameJNIComponentsRecipe, self).prebuild_arch(arch)

        info('Unpacking pygame bootstrap JNI dir components')
        with current_directory(self.get_build_container_dir(arch)):
            if exists('sdl'):
                info('sdl dir exists, so it looks like the JNI components' +
                     'are already unpacked. Skipping.')
                return
            for dirn in glob.glob(join(self.get_build_dir(arch),
                                       'pygame_bootstrap_jni', '*')):
                shprint(sh.mv, dirn, './')
        info('Unpacking was successful, deleting original container dir')
        shprint(sh.rm, '-rf', self.get_build_dir(arch))

    def apply_patches(self, arch, build_dir=None):
        super(PygameJNIComponentsRecipe, self).apply_patches(
            arch, build_dir=self.get_build_container_dir(arch.arch))


recipe = PygameJNIComponentsRecipe()
