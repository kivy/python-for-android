import glob
from logging import info

import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe
from pythonforandroid.util import current_directory


class GrpcioRecipe(CppCompiledComponentsPythonRecipe):
    version = '1.64.0'
    url = 'https://files.pythonhosted.org/packages/source/g/grpcio/grpcio-{version}.tar.gz'
    depends = ["setuptools", "librt", "libpthread"]
    patches = ["comment-getserverbyport-r-args.patch", "remove-android-log-write.patch"]

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env['NDKPLATFORM'] = "NOTNONE"
        env['GRPC_PYTHON_BUILD_WITH_CYTHON'] = '1'
        env["CFLAGS"] += " -U__ANDROID_API__"
        env["CFLAGS"] += " -D__ANDROID_API__={}".format(self.ctx.ndk_api)

        # turn off c++11 warning error of "invalid suffix on literal"
        env["CFLAGS"] += " -Wno-reserved-user-defined-literal"
        env['PLATFORM'] = 'android'
        env["LDFLAGS"] += " -llog -landroid"
        return env

    def build_compiled_components(self, arch):
        info('Building compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        hostpython = sh.Command(self.hostpython_location)
        with current_directory(self.get_build_dir(arch.arch)):
            if self.install_in_hostpython:
                shprint(hostpython, 'setup.py', 'clean', '--all', _env=env)
            shprint(hostpython, 'setup.py', self.build_cmd, '-v',
                    _env=env, *self.setup_extra_args)

            # grpcio creates a build directory and names it `pyb`
            build_dir = glob.glob('pyb/lib.*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)


recipe = GrpcioRecipe()
