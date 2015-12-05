
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe, shprint, current_directory, warning
from os.path import exists, join
import sh
import glob


class NumpyRecipe(CompiledComponentsPythonRecipe):
    
    version = '1.9.2'
    url = 'http://pypi.python.org/packages/source/n/numpy/numpy-{version}.tar.gz'
    site_packages_name= 'numpy'

    depends = ['python2']

    def prebuild_arch(self, arch):
        super(NumpyRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('numpy already patched, skipping')
            return

        self.apply_patch('patches/fix-numpy.patch', arch.arch)
        self.apply_patch('patches/prevent_libs_check.patch', arch.arch)
        self.apply_patch('patches/ar.patch', arch.arch)
        self.apply_patch('patches/lib.patch', arch.arch)

        # AND: Fix this warning!
        warning('Numpy is built assuming the archiver name is '
                'arm-linux-androideabi-ar, which may not always be true!')

        shprint(sh.touch, join(build_dir, '.patched'))


recipe = NumpyRecipe()
