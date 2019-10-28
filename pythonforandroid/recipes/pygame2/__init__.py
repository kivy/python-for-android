from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join
from shutil import copyfile
from pythonforandroid.toolchain import current_directory
import glob

class Pygame2Recipe(CompiledComponentsPythonRecipe):

    version = '2.0.0-dev5'
    url = 'https://github.com/pygame/pygame/archive/android.zip'

    site_packages_name = 'pygame'
    name = 'pygame2'

    depends = ['sdl2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf', 'setuptools']
    call_hostpython_via_targetpython = False  # Due to setuptools
    install_in_hostpython = False

    def cythonize_file(self, env, build_dir, filename):
        # We can ignore a few files that aren't important to the
        # android build, and may not work on Android anyway
        do_not_cythonize = []
        if basename(filename) in do_not_cythonize:
            return
        super(Pygame2Recipe, self).cythonize_file(env, build_dir, filename)

    def prebuild_arch(self, arch):
        super(Pygame2Recipe, self).prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            setup_template=open(join("buildconfig", "Setup.Android.SDL2.in")).read()
            env=self.get_recipe_env(arch)
            setup_file=setup_template.format(
                sdl_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include') +
                    " -L" + join(self.ctx.bootstrap.build_dir, "libs", str(arch))),
                sdl_ttf_includes="-I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                sdl_image_includes="-I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
                sdl_mixer_includes="-I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'))
            open("Setup", "w").write(setup_file)

    def get_recipe_env(self, arch):
        env = super(Pygame2Recipe, self).get_recipe_env(arch)
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'

            env["PYGAME_CROSS_COMPILE"]="TRUE"
            env["PYGAME_ANDROID"]="TRUE"
        return env
    
recipe = Pygame2Recipe()
