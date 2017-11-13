
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

    def prebuild_arch(self, arch):
        super(NumpyRecipe, self).prebuild_arch(arch)

        warning('Numpy is built assuming the archiver name is '
                'arm-linux-androideabi-ar, which may not always be true!')


recipe = NumpyRecipe()
