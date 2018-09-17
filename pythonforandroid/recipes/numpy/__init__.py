from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import warning
from os.path import join


class NumpyRecipe(CompiledComponentsPythonRecipe):

    version = '1.15.1'
    url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.zip'
    site_packages_name = 'numpy'

    depends = [('python2', 'python3crystax')]

    patches = [
        join('patches', 'fix-numpy.patch'),
        join('patches', 'prevent_libs_check.patch'),
        join('patches', 'ar.patch'),
        join('patches', 'lib.patch'),
        join('patches', 'python2-fixes.patch')
    ]

    def get_recipe_env(self, arch):
        env = super(NumpyRecipe, self).get_recipe_env(arch)

        flags = " -L{} --sysroot={}".format(
            join(self.ctx.ndk_platform, 'usr', 'lib'),
            self.ctx.ndk_platform
        )

        if self.ctx.ndk == 'crystax':
            py_ver = self.ctx.python_recipe.version[0:3]
            src_dir = join(self.ctx.ndk_dir, 'sources')
            py_inc_dir = join(src_dir, 'python', py_ver, 'include', 'python')
            py_lib_dir = join(src_dir, 'python', py_ver, 'libs', arch.arch)
            cry_inc_dir = join(src_dir, 'crystax', 'include')
            cry_lib_dir = join(src_dir, 'crystax', 'libs', arch.arch)
            flags += ' -I{}'.format(py_inc_dir)
            flags += ' -L{} -lpython{}m'.format(py_lib_dir, py_ver)
            flags += " -I{}".format(cry_inc_dir)
            flags += " -L{}".format(cry_lib_dir)

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
