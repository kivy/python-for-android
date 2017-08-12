from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory, shutil
from pythonforandroid.util import ensure_dir
from os.path import exists, join, dirname
import sh
from multiprocessing import cpu_count


from pythonforandroid.toolchain import info


class ProtobufCppRecipe(PythonRecipe):
    name = 'protobuf_cpp'
    version = '3.1.0'
    url = 'https://github.com/google/protobuf/releases/download/v{version}/protobuf-python-{version}.tar.gz'
    call_hostpython_via_targetpython = False
    depends = ['cffi', 'setuptools']
    site_packages_name = 'google/protobuf/pyext'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        # Build libproto.a
        with current_directory(self.get_build_dir(arch.arch)):
            env['HOSTARCH'] = 'arm-eabi'
            env['BUILDARCH'] = shprint(sh.gcc, '-dumpmachine').stdout.decode('utf-8').split('\n')[0]

            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)

            shprint(sh.Command('./configure'),
                                '--host={}'.format(env['HOSTARCH']),
                                '--enable-shared',
                                _env=env)

            with current_directory(join(self.get_build_dir(arch.arch), 'src')):
                shprint(sh.make, 'libprotobuf.la', '-j'+str(cpu_count()), _env=env)
                shprint(sh.cp, '.libs/libprotobuf.a', join(self.ctx.get_libs_dir(arch.arch), 'libprotobuf.a'))

        # Copy stl library
                shutil.copyfile(self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + '/libgnustl_shared.so',
                    join(self.ctx.get_libs_dir(arch.arch), 'libgnustl_shared.so'))

        # Build python bindings and _message.so
        with current_directory(join(self.get_build_dir(arch.arch), 'python')):
            hostpython = sh.Command(self.hostpython_location)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    '--cpp_implementation'
                    , _env=env)

        # Install python bindings
        self.install_python_package(arch)


    def install_python_package(self, arch):
        env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(join(self.get_build_dir(arch.arch), 'python')):
            hostpython = sh.Command(self.hostpython_location)

            if self.ctx.python_recipe.from_crystax:
                hpenv = env.copy()
                shprint(hostpython, 'setup.py', 'install', '-O2',
                        '--root={}'.format(self.ctx.get_python_install_dir()),
                        '--install-lib=.',
                        '--cpp_implementation',
                        _env=hpenv, *self.setup_extra_args)
            else:
                hppath = join(dirname(self.hostpython_location), 'Lib',
                              'site-packages')
                hpenv = env.copy()
                if 'PYTHONPATH' in hpenv:
                    hpenv['PYTHONPATH'] = ':'.join([hppath] +
                                                   hpenv['PYTHONPATH'].split(':'))
                else:
                    hpenv['PYTHONPATH'] = hppath
                shprint(hostpython, 'setup.py', 'install', '-O2',
                        '--root={}'.format(self.ctx.get_python_install_dir()),
                        '--install-lib=lib/python2.7/site-packages',
                        '--cpp_implementation',
                        _env=hpenv, *self.setup_extra_args)


    def get_recipe_env(self, arch):
        env = super(ProtobufCppRecipe, self).get_recipe_env(arch)
        env['PROTOC'] = '/home/fipo/soft/protobuf-3.1.0/src/protoc'
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['TARGET_OS'] = 'OS_ANDROID_CROSSCOMPILE'
        env['CFLAGS'] += ' -I' + self.ctx.ndk_dir + '/platforms/android-' + str(
            self.ctx.android_api) + '/arch-' + arch.arch.replace('eabi', '') + '/usr/include' + \
                         ' -I' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/include' + \
                         ' -I' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + '/include' + \
                         ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['CXXFLAGS'] = env['CFLAGS']
        env['CXXFLAGS'] += ' -frtti'
        env['CXXFLAGS'] += ' -fexceptions'
        env['LDFLAGS'] += ' -L' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + \
                          ' -lgnustl_shared -lpython2.7'

        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        return env


recipe = ProtobufCppRecipe()
