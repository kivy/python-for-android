import glob
from os.path import basename, exists, join
import sys
import packaging.version

import sh
from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.toolchain import current_directory, shprint


def is_kivy_affected_by_deadlock_issue(recipe=None, arch=None):
    with current_directory(join(recipe.get_build_dir(arch.arch), "kivy")):
        kivy_version = shprint(
            sh.Command(sys.executable),
            "-c",
            "import _version; print(_version.__version__)",
        )

        return packaging.version.parse(
            str(kivy_version)
        ) < packaging.version.Version("2.2.0.dev0")


class KivyRecipe(CythonRecipe):
    version = '2.3.0'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = ['sdl2', 'pyjnius', 'setuptools']
    python_depends = ['certifi', 'chardet', 'idna', 'requests', 'urllib3']

    # sdl-gl-swapwindow-nogil.patch is needed to avoid a deadlock.
    # See: https://github.com/kivy/kivy/pull/8025
    # WARNING: Remove this patch when a new Kivy version is released.
    patches = [("sdl-gl-swapwindow-nogil.patch", is_kivy_affected_by_deadlock_issue)]

    def cythonize_build(self, env, build_dir='.'):
        super().cythonize_build(env, build_dir=build_dir)

        if not exists(join(build_dir, 'kivy', 'include')):
            return

        # If kivy is new enough to use the include dir, copy it
        # manually to the right location as we bypass this stage of
        # the build
        with current_directory(build_dir):
            build_libs_dirs = glob.glob(join('build', 'lib.*'))

            for dirn in build_libs_dirs:
                shprint(sh.cp, '-r', join('kivy', 'include'),
                        join(dirn, 'kivy'))

    def cythonize_file(self, env, build_dir, filename):
        # We can ignore a few files that aren't important to the
        # android build, and may not work on Android anyway
        do_not_cythonize = ['window_x11.pyx', ]
        if basename(filename) in do_not_cythonize:
            return
        super().cythonize_file(env, build_dir, filename)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SPLIT_EXAMPLES'] = '1'
            sdl2_mixer_recipe = self.get_recipe('sdl2_mixer', self.ctx)
            sdl2_image_recipe = self.get_recipe('sdl2_image', self.ctx)
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                *sdl2_image_recipe.get_include_dirs(arch),
                *sdl2_mixer_recipe.get_include_dirs(arch),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
            ])

        return env


recipe = KivyRecipe()
