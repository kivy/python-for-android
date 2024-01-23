from multiprocessing import cpu_count
from os.path import join
from os import environ
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe
from pythonforandroid.util import build_platform, current_directory


def arch_to_toolchain(arch):
    if 'arm' in arch.arch:
        return arch.command_prefix
    return arch.arch


class ScipyRecipe(CompiledComponentsPythonRecipe):

    version = 'maintenance/1.11.x'
    url = 'git+https://github.com/scipy/scipy.git'
    git_commit = 'b430bf54b5064465983813e2cfef3fcb86c3df07'  # version 1.11.3
    site_packages_name = 'scipy'
    depends = ['setuptools', 'cython', 'numpy', 'lapack', 'pybind11']
    call_hostpython_via_targetpython = False
    need_stl_shared = True
    patches = ["setup.py.patch"]

    def build_compiled_components(self, arch):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().build_compiled_components(arch)
        self.setup_extra_args = []

    def rebuild_compiled_components(self, arch, env):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().rebuild_compiled_components(arch, env)
        self.setup_extra_args = []

    def download_file(self, url, target, cwd=None):
        super().download_file(url, target, cwd=cwd)
        with current_directory(target):
            shprint(sh.git, 'fetch', '--unshallow')
            shprint(sh.git, 'checkout', self.git_commit)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        arch_env = arch.get_env()

        env['LDFLAGS'] = arch_env['LDFLAGS']
        env['LDFLAGS'] += ' -L{} -lpython{}'.format(
            self.ctx.python_recipe.link_root(arch.arch),
            self.ctx.python_recipe.link_version,
        )

        ndk_dir = environ["LEGACY_NDK"]
        GCC_VER = '4.9'
        HOST = build_platform
        suffix = '64' if '64' in arch.arch else ''

        prefix = arch.command_prefix
        CLANG_BIN = f'{ndk_dir}/toolchains/llvm/prebuilt/{HOST}/bin/'
        GCC = f'{ndk_dir}/toolchains/{arch_to_toolchain(arch)}-{GCC_VER}/prebuilt/{HOST}'
        libgfortran = f'{GCC}/{prefix}/lib{suffix}'
        numpylib = self.ctx.get_python_install_dir(arch.arch) + '/numpy'
        arch_cflags = ' '.join(arch.arch_cflags)
        LDSHARED_opts = f'-target {arch.target} {arch_cflags} ' + ' '.join(arch.common_ldshared)

        # TODO: add pythran support
        env['SCIPY_USE_PYTHRAN'] = '0'

        lapack_dir = join(Recipe.get_recipe('lapack', self.ctx).get_build_dir(arch.arch), 'build', 'install')
        env['LAPACK'] = f'{lapack_dir}/lib'
        env['BLAS'] = env['LAPACK']

        # compilers
        env['F77'] = f'{GCC}/bin/{prefix}-gfortran'
        env['F90'] = f'{GCC}/bin/{prefix}-gfortran'
        env['CC'] = f'{CLANG_BIN}clang -target {arch.target} {arch_cflags}'
        env['CXX'] = f'{CLANG_BIN}clang++ -target {arch.target} {arch_cflags}'

        # scipy expects ldshared to be a single executable without options
        env['LDSHARED'] = f'{CLANG_BIN}/clang'

        # erase the default NDK C++ include options
        env['CPPFLAGS'] = '-DANDROID'

        # configure linker
        env['LDFLAGS'] += f' {LDSHARED_opts} -L{libgfortran} -L{numpylib}/core/lib -L{numpylib}/random/lib'
        env['LDFLAGS'] += f' -l{self.stl_lib_name}'
        return env


recipe = ScipyRecipe()
