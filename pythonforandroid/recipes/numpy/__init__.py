from pythonforandroid.toolchain import CompiledComponentsPythonRecipe, warning

class NumpyRecipe(CompiledComponentsPythonRecipe):
    version = '1.9.2'
    url = 'http://pypi.python.org/packages/source/n/numpy/numpy-{version}.tar.gz'
    site_packages_name= 'numpy'
    depends = ['python2']
    call_hostpython_via_targetpython = False

    patches = ['patches/fix-numpy.patch',
               'patches/prevent_libs_check.patch',
               'patches/ar.patch',
               'patches/lib.patch']

    def prebuild_arch(self, arch):
        super(NumpyRecipe, self).prebuild_arch(arch)
        # AND: Fix this warning!
        warning('Numpy is built assuming the archiver name is '
                'arm-linux-androideabi-ar, which may not always be true!')

    def get_recipe_env(self, arch):
        env = super(NumpyRecipe, self).get_recipe_env(arch)
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        return env

recipe = NumpyRecipe()
