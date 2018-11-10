from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.logger import shprint, info_notify
from pythonforandroid.util import current_directory, shutil
from os.path import exists, join, dirname
import sh
from multiprocessing import cpu_count
from pythonforandroid.toolchain import info
import sys
import os


class ProtobufCppRecipe(PythonRecipe):
    name = 'protobuf_cpp'
    version = '3.5.1'
    url = 'https://github.com/google/protobuf/releases/download/v{version}/protobuf-python-{version}.tar.gz'
    call_hostpython_via_targetpython = False
    depends = ['cffi', 'setuptools']
    site_packages_name = 'google/protobuf/pyext'
    protoc_dir = None

    def prebuild_arch(self, arch):
        super(ProtobufCppRecipe, self).prebuild_arch(arch)
        # During building, host needs to transpile .proto files to .py
        # ideally with the same version as protobuf runtime, or with an older one.
        # Because protoc is compiled for target (i.e. Android), we need an other binary
        # which can be run by host.
        # To make it easier, we download prebuild protoc binary adapted to the platform

        info_notify("Downloading protoc compiler for your platform")
        url_prefix = "https://github.com/protocolbuffers/protobuf/releases/download/v{version}".format(version=self.version)
        if sys.platform.startswith('linux'):
            info_notify("GNU/Linux detected")
            filename = "protoc-{version}-linux-x86_64.zip".format(version=self.version)
        elif sys.platform.startswith('darwin'):
            info_notify("Mac OS X detected")
            filename = "protoc-{version}-osx-x86_64.zip".format(version=self.version)
        else:
            info_notify("Your platform is not supported, but recipe can still "
                        "be built if you have a valid protoc (<={version}) in "
                        "your path".format(version=self.version))
            return

        protoc_url = join(url_prefix, filename)
        self.protoc_dir = join(self.ctx.build_dir, "tools", "protoc")
        if os.path.exists(join(self.protoc_dir, "bin", "protoc")):
            info_notify("protoc found, no download needed")
            return
        try:
            os.makedirs(self.protoc_dir)
        except OSError as e:
            # if dir already exists (errno 17), we ignore the error
            if e.errno != 17:
                raise e
        info_notify("Will download into {dest_dir}".format(dest_dir=self.protoc_dir))
        self.download_file(protoc_url, join(self.protoc_dir, filename))
        with current_directory(self.protoc_dir):
            shprint(sh.unzip, join(self.protoc_dir, filename))

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
                shutil.copyfile(
                    self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + '/libgnustl_shared.so',
                    join(self.ctx.get_libs_dir(arch.arch), 'libgnustl_shared.so'))

        # Build python bindings and _message.so
        with current_directory(join(self.get_build_dir(arch.arch), 'python')):
            hostpython = sh.Command(self.hostpython_location)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    '--cpp_implementation', _env=env)

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
        if self.protoc_dir is not None:
            # we need protoc with binary for host platform
            env['PROTOC'] = join(self.protoc_dir, 'bin', 'protoc')
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['TARGET_OS'] = 'OS_ANDROID_CROSSCOMPILE'
        env['CFLAGS'] += (
            ' -I' + self.ctx.ndk_dir + '/platforms/android-' +
            str(self.ctx.android_api) +
            '/arch-' + arch.arch.replace('eabi', '') + '/usr/include' +
            ' -I' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' +
            self.ctx.toolchain_version + '/include' +
            ' -I' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' +
            self.ctx.toolchain_version + '/libs/' + arch.arch + '/include' +
            ' -I' + env['PYTHON_ROOT'] + '/include/python2.7')
        env['CXXFLAGS'] = env['CFLAGS']
        env['CXXFLAGS'] += ' -frtti'
        env['CXXFLAGS'] += ' -fexceptions'
        env['LDFLAGS'] += (
            ' -L' + self.ctx.ndk_dir +
            '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version +
            '/libs/' + arch.arch + ' -lgnustl_shared -lpython2.7 -landroid -llog')

        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        return env


recipe = ProtobufCppRecipe()
