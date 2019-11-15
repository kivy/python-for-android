from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join
from pythonforandroid.toolchain import current_directory


class Pygame2Recipe(CompiledComponentsPythonRecipe):

    version = '2.0.0-dev7'
    url = 'https://github.com/pygame/pygame/archive/android.zip'

    site_packages_name = 'pygame'
    name = 'pygame2'

    depends = ['sdl2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf', 'setuptools', 'jpeg', 'png']
    call_hostpython_via_targetpython = False  # Due to setuptools
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super(Pygame2Recipe, self).prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            setup_template = open(join("buildconfig", "Setup.Android.SDL2.in")).read()
            env = self.get_recipe_env(arch)
            env['ANDROID_ROOT'] = join(self.ctx.ndk_platform, 'usr')

            ndk_lib_dir = join(self.ctx.ndk_platform, 'usr', 'lib')
            ndk_include_dir = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')

            png = self.get_recipe('png', self.ctx)
            png_lib_dir = join(png.get_build_dir(arch.arch), '.libs')
            png_inc_dir = png.get_build_dir(arch)

            jpeg = self.get_recipe('jpeg', self.ctx)
            jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)

            setup_file = setup_template.format(
                sdl_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include') +
                    " -L" + join(self.ctx.bootstrap.build_dir, "libs", str(arch)) +
                    " -L" + png_lib_dir+ " -L" + jpeg_lib_dir+ " -L" + ndk_lib_dir ),
                sdl_ttf_includes=" -I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                sdl_image_includes="-I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
                sdl_mixer_includes="-I"+join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
                jpeg_includes="-I"+jpeg_inc_dir,
                png_includes="-I"+png_inc_dir,
                freetype_includes=""
            )
            open("Setup", "w").write(setup_file)

    def get_recipe_env(self, arch):
        env = super(Pygame2Recipe, self).get_recipe_env(arch)
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env["PYGAME_CROSS_COMPILE"] = "TRUE"
            env["PYGAME_ANDROID"] = "TRUE"
        return env


recipe = Pygame2Recipe()
