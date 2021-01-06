from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe
from multiprocessing import cpu_count
from os.path import join


class ScipyRecipe(CompiledComponentsPythonRecipe):

    version = '1.5.4'
    url = f'https://github.com/scipy/scipy/releases/download/v{version}/scipy-{version}.zip'
    site_packages_name = 'scipy'
    depends = ['setuptools', 'cython', 'numpy', 'lapack']
    call_hostpython_via_targetpython = False

    def build_compiled_components(self, arch):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().build_compiled_components(arch)
        self.setup_extra_args = []

    def rebuild_compiled_components(self, arch, env):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().rebuild_compiled_components(arch, env)
        self.setup_extra_args = []

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        GCC_VER = '4.9'
        HOST = 'linux-x86_64'
        LIB = 'lib64' if '64' in arch.arch else 'lib'

        prefix = env['TOOLCHAIN_PREFIX']
        lapack_dir = join(Recipe.get_recipe('lapack', self.ctx).get_build_dir(arch.arch), 'build', 'install')
        sysroot = f"{self.ctx.ndk_dir}/platforms/{env['NDK_API']}/{arch.platform_dir}"
        sysroot_include = f'{self.ctx.ndk_dir}/toolchains/llvm/prebuilt/{HOST}/sysroot/usr/include'
        libgfortran = f'{self.ctx.ndk_dir}/toolchains/{prefix}-{GCC_VER}/prebuilt/{HOST}/{prefix}/{LIB}'
        numpylib = self.ctx.get_python_install_dir() + '/numpy/core/lib'
        LDSHARED_opts = env['LDSHARED'].split('clang')[1]

        env['LAPACK'] = f'{lapack_dir}/lib'
        env['BLAS'] = env['LAPACK']
        env['F90'] = f'{prefix}-gfortran'
        env['CXX'] += f' -Wl,-l{self.stl_lib_name} -Wl,-L{self.get_stl_lib_dir(arch)}'
        env['CPPFLAGS'] += f' --sysroot={sysroot} -I{sysroot_include}/c++/v1 -I{sysroot_include}'
        env['LDSHARED'] = 'clang'
        env['LDFLAGS'] += f' {LDSHARED_opts} --sysroot={sysroot} -L{libgfortran} -L{numpylib}'
        env['LDFLAGS'] += f' -L{self.ctx.ndk_dir}/sources/cxx-stl/llvm-libc++/libs/{arch.arch}/'

        return env


recipe = ScipyRecipe()
