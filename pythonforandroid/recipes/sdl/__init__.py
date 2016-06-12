from pythonforandroid.toolchain import BootstrapNDKRecipe, shprint, current_directory, info, info_main, ensure_dir
from os.path import exists, join
import sh


class LibSDLRecipe(BootstrapNDKRecipe):
    version = "1.2.14"
    url = None  
    name = 'sdl'
    dir_name = 'sdl'
    depends = ['python2', 'pygame_bootstrap_components', 'jpeg', 'freetype']
    conflicts = ['sdl2']

    def prebuild_arch(self, arch):
        super(LibSDLRecipe, self).prebuild_arch(arch)

        # Patch sdl_image and sdl_ttf to support new libraries
        if exists(join(self.get_jni_dir(), 'sdl', '.patched')):
            info_main('sdl already patched, skipping')
            return
        for patch_dir, patch in [('sdl_image', 'jpeg-prebuilt.patch'),
                                 ('sdl_ttf', 'freetype-prebuilt.patch')]:
            shprint(sh.patch, "-t", "-d", join(self.get_jni_dir(), patch_dir), "-p1",
                        "-i", join(self.recipe_dir, patch), _tail=10)
        shprint(sh.touch, join(self.get_jni_dir(), 'sdl', '.patched'))

    def get_recipe_env(self, arch=None):
        env = super(LibSDLRecipe, self).get_recipe_env(arch)

        env['WITH_HARFBUZZ_SUPPORT'] = 'false'
        if 'harfbuzz' in self.ctx.recipe_build_order:
            env['WITH_HARFBUZZ_SUPPORT'] = 'true'

        return env

    def build_arch(self, arch):

        if exists(join(self.ctx.libs_dir, 'libsdl.so')):
            info('libsdl.so already exists, skipping sdl build.')
            return

        # Patch Python Install Directory
        python_build_name = self.get_recipe('python2', arch.arch).get_dir_name()
        shprint(sh.sed, '-i', 's#other_builds/python2/#other_builds/{}/#'.format(python_build_name),
                join(self.get_jni_dir(), 'application/Android.mk'))

        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, 'V=1', _env=env, _tail=20, _critical=True)

        import os
        libs_dir = join(self.ctx.bootstrap.build_dir, 'libs', arch.arch)
        contents = list(os.walk(libs_dir))[0][-1]

        libs_target = join(self.ctx.build_dir, 'libs_collections',
                        self.ctx.bootstrap.distribution.name, arch.arch)
        ensure_dir(libs_target)
        for content in contents:
            shprint(sh.cp, '-a', join(self.ctx.bootstrap.build_dir, 'libs',
                                      arch.arch, content), libs_target)


recipe = LibSDLRecipe()
