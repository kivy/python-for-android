
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe, warning


class NumpyRecipe(CompiledComponentsPythonRecipe):
    
    version = '1.9.2'
    url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.tar.gz'
    site_packages_name= 'numpy'

    depends = ['python2']

    patches = ['patches/fix-numpy.patch',
               'patches/prevent_libs_check.patch',
               'patches/ar.patch',
               'patches/lib.patch']

    def get_recipe_env(self, arch):
        """ looks like numpy has no proper -L flags. Code copied and adapted from 
            https://github.com/frmdstryr/p4a-numpy/
        """

        env = super(NumpyRecipe, self).get_recipe_env(arch)
        #: Hack add path L to crystax as a CFLAG

        py_ver = '3.5'
        if {'python2crystax', 'python2'} & set(self.ctx.recipe_build_order):
            py_ver = '2.7'

        py_so = '2.7' if py_ver == '2.7' else '3.5m'
    
        api_ver = self.ctx.android_api

        platform = 'arm' if 'arm' in arch.arch else arch.arch
        #: Not sure why but we have to inject these into the CC and LD env's for it to
        #: use the correct arguments.
        flags = " -L{ctx.ndk_dir}/platforms/android-{api_ver}/arch-{platform}/usr/lib/" \
                " --sysroot={ctx.ndk_dir}/platforms/android-{api_ver}/arch-{platform}" \
            .format(ctx=self.ctx, arch=arch, platform=platform, api_ver=api_ver,
                    py_so=py_so, py_ver=py_ver)
        if flags not in env['CC']:
            env['CC'] += flags
        if flags not in env['LD']:
            env['LD'] += flags + ' -shared'

        return env

    def prebuild_arch(self, arch):
        super(NumpyRecipe, self).prebuild_arch(arch)

        warning('Numpy is built assuming the archiver name is '
                'arm-linux-androideabi-ar, which may not always be true!')


recipe = NumpyRecipe()
