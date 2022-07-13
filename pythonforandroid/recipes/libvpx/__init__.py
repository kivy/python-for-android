from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
from os.path import join, realpath
from multiprocessing import cpu_count
import sh


TARGETS = {
    'armeabi-v7a': 'armv7-android-gcc',
    'arm64-v8a': 'arm64-android-gcc',
    'x86': 'x86-android-gcc',
    'x86_64': 'x86_64-android-gcc',
}


class VPXRecipe(Recipe):
    version = '1.11.0'
    url = 'https://github.com/webmproject/libvpx/archive/v{version}.tar.gz'

    patches = [
        # See https://git.io/Jq50q
        join('patches', '0001-android-force-neon-runtime.patch'),
    ]

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['CXXFLAGS'] += f' -I{self.ctx.ndk.libcxx_include_dir}'
        return env

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            flags = [
                '--target=' + TARGETS[arch.arch],
                '--enable-pic',
                '--enable-vp8',
                '--enable-vp9',
                '--enable-static',
                '--enable-small',
                '--disable-shared',
                '--disable-examples',
                '--disable-unit-tests',
                '--disable-tools',
                '--disable-docs',
                '--disable-install-docs',
                '--disable-realtime-only',
                '--enable-external-build',
                f'--prefix={realpath(".")}',
            ]
            configure = sh.Command('./configure')
            shprint(configure, *flags, _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = VPXRecipe()
