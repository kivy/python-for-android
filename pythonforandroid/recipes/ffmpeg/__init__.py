from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import join, exists
import sh

"""
FFmpeg for Android compiled with x264, libass, fontconfig, freetype, fribidi and lame (Supports Android 4.1+)

http://writingminds.github.io/ffmpeg-android/
"""
class FFMpegRecipe(Recipe):

    version = 'master'
    url = 'git+https://github.com/WritingMinds/ffmpeg-android.git'
    patches = ['settings.patch']


    def should_build(self, arch):
        return not exists(self.get_build_bin(arch))


    def build_arch(self, arch):
        super(FFMpegRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
            bash = sh.Command('bash')
            shprint(bash, 'init_update_libs.sh')
            shprint(bash, 'android_build.sh', _env=env)


    def get_build_bin(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return join(build_dir, 'build', arch.arch, 'bin', 'ffmpeg')


    def get_recipe_env(self, arch):
        env = super(FFMpegRecipe, self).get_recipe_env(arch)
        env['ANDROID_NDK'] = self.ctx.ndk_dir
        env['ANDROID_API'] = str(self.ctx.android_api)
        return env


recipe = FFMpegRecipe()