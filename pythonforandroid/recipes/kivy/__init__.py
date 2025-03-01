import glob
from os.path import basename, exists, join
import sys
import packaging.version

import sh
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.toolchain import current_directory, shprint


class KivyRecipe(PyProjectRecipe):
    version = 'master'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    depends = ['sdl2', 'pyjnius']
    python_depends = ['certifi', 'chardet', 'idna', 'requests', 'urllib3', 'filetype']
    patches = ["use_cython.patch"]
    
    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        env['LIBLINK'] = "NOTNONE"
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SPLIT_EXAMPLES'] = '1'
            sdl_recipe = self.get_recipe("sdl2", self.ctx)
            sdl2_mixer_recipe = self.get_recipe('sdl2_mixer', self.ctx)
            sdl2_image_recipe = self.get_recipe('sdl2_image', self.ctx)
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                *sdl2_image_recipe.get_include_dirs(arch),
                *sdl2_mixer_recipe.get_include_dirs(arch),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
            ])
            env["LDFLAGS"] += " -L" + join(sdl_recipe.get_build_dir(arch.arch), "../..", "libs", arch.arch)
        return env


recipe = KivyRecipe()
