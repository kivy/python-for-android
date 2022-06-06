from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe
from multiprocessing import cpu_count
from os.path import join
from os import environ
from pythonforandroid.util import build_platform

arch_to_sysroot = {'armeabi': 'arm', 'armeabi-v7a': 'arm', 'arm64-v8a': 'arm64'}


class ScipyRecipe(CompiledComponentsPythonRecipe):

    version = '1.8.1'
    url = f'https://github.com/scipy/scipy/releases/download/v{version}/scipy-{version}.zip'
    site_packages_name = 'scipy'
    depends = ['setuptools', 'cython', 'numpy', 'lapack', 'pybind11']
    call_hostpython_via_targetpython = False
    need_stl_shared = True

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

        ndk_dir = environ["LEGACY_NDK"]
        GCC_VER = '4.9'
        HOST = build_platform
        suffix = '64' if '64' in arch.arch else ''

        prefix = arch.command_prefix
        sysroot_suffix = arch_to_sysroot.get(arch.arch, arch.arch)
        sysroot = f"{ndk_dir}/platforms/{env['NDK_API']}/arch-{sysroot_suffix}"
        sysroot_include = f'{ndk_dir}/toolchains/llvm/prebuilt/{HOST}/sysroot/usr/include'
        CLANG_BIN = f'{ndk_dir}/toolchains/llvm/prebuilt/{HOST}/bin/'
        GCC = f'{ndk_dir}/toolchains/{prefix}-{GCC_VER}/prebuilt/{HOST}'
        libgfortran = f'{GCC}/{prefix}/lib{suffix}'

        numpylib = self.ctx.get_python_install_dir(arch.arch) + '/numpy'
        LDSHARED_opts = env['LDSHARED'].split('clang')[1]
        arch_cflags = ' '.join(arch.arch_cflags)

        # TODO: add pythran support
        env['SCIPY_USE_PYTHRAN'] = '0'

        lapack_dir = join(Recipe.get_recipe('lapack', self.ctx).get_build_dir(arch.arch), 'build', 'install')
        env['LAPACK'] = f'{lapack_dir}/lib'
        env['BLAS'] = env['LAPACK']

        # compilers
        env['F77'] = f'{GCC}/bin/{prefix}-gfortran'
        env['F90'] = f'{GCC}/bin/{prefix}-gfortran'
        env['CC'] = f'{CLANG_BIN}/clang -target {arch.target} {arch_cflags}'
        env['CXX'] = f'{CLANG_BIN}/clang++ -target {arch.target} {arch_cflags}'
        env['LDSHARED'] = f'{CLANG_BIN}/clang'

        # flags
        env['CPPFLAGS'] = f'-DANDROID -I{sysroot_include}/{prefix} --sysroot={sysroot} -I{sysroot_include}/c++/v1 -I{sysroot_include}'
        env['LDFLAGS'] += f' {LDSHARED_opts} --sysroot={sysroot} -L{libgfortran} -L{numpylib}/core/lib -L{numpylib}/random/lib'
        env['LDFLAGS'] += f' -l{self.stl_lib_name} '
        env['LDFLAGS'] += f' -L{ndk_dir}/sources/cxx-stl/llvm-libc++/libs/{arch.arch}/'  # for arm32 - unwind
        return env


recipe = ScipyRecipe()
