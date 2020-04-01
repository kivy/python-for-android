from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe
from pythonforandroid.logger import shprint, info_notify
from pythonforandroid.util import current_directory
from os.path import exists, join
import sh
from multiprocessing import cpu_count
from pythonforandroid.toolchain import info
import sys
import os


class ProtobufCppRecipe(CppCompiledComponentsPythonRecipe):
    """This is a two-in-one recipe:
      - build labraru `libprotobuf.so`
      - build and install python binding for protobuf_cpp
    """
    name = 'protobuf_cpp'
    version = '3.6.1'
    url = 'https://github.com/google/protobuf/releases/download/v{version}/protobuf-python-{version}.tar.gz'
    call_hostpython_via_targetpython = False
    depends = ['cffi', 'setuptools']
    site_packages_name = 'google/protobuf/pyext'
    setup_extra_args = ['--cpp_implementation']
    built_libraries = {'libprotobuf.so': 'src/.libs'}
    protoc_dir = None

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)

        patch_mark = join(self.get_build_dir(arch.arch), '.protobuf-patched')
        if self.ctx.python_recipe.name == 'python3' and not exists(patch_mark):
            self.apply_patch('fix-python3-compatibility.patch', arch.arch)
            shprint(sh.touch, patch_mark)

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

        # Build libproto.so
        with current_directory(self.get_build_dir(arch.arch)):
            build_arch = (
                shprint(sh.gcc, '-dumpmachine')
                .stdout.decode('utf-8')
                .split('\n')[0]
            )

            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)

            shprint(sh.Command('./configure'),
                    '--build={}'.format(build_arch),
                    '--host={}'.format(arch.command_prefix),
                    '--target={}'.format(arch.command_prefix),
                    '--disable-static',
                    '--enable-shared',
                    _env=env)

            with current_directory(join(self.get_build_dir(arch.arch), 'src')):
                shprint(sh.make, 'libprotobuf.la', '-j'+str(cpu_count()), _env=env)

        self.install_python_package(arch)

    def build_compiled_components(self, arch):
        # Build python bindings and _message.so
        env = self.get_recipe_env(arch)
        with current_directory(join(self.get_build_dir(arch.arch), 'python')):
            hostpython = sh.Command(self.hostpython_location)
            shprint(hostpython,
                    'setup.py',
                    'build_ext',
                    _env=env, *self.setup_extra_args)

    def install_python_package(self, arch):
        env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(join(self.get_build_dir(arch.arch), 'python')):
            hostpython = sh.Command(self.hostpython_location)

            hpenv = env.copy()
            shprint(hostpython, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir()),
                    '--install-lib=.',
                    _env=hpenv, *self.setup_extra_args)

        # Create __init__.py which is missing, see also:
        #   - https://github.com/protocolbuffers/protobuf/issues/1296
        #   - https://stackoverflow.com/questions/13862562/
        #   google-protocol-buffers-not-found-when-trying-to-freeze-python-app
        open(
            join(self.ctx.get_site_packages_dir(), 'google', '__init__.py'),
            'a',
        ).close()

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        if self.protoc_dir is not None:
            # we need protoc with binary for host platform
            env['PROTOC'] = join(self.protoc_dir, 'bin', 'protoc')
        env['TARGET_OS'] = 'OS_ANDROID_CROSSCOMPILE'
        env['CXXFLAGS'] += ' -std=c++11'
        env['LDFLAGS'] += ' -lm -landroid -llog'
        return env


recipe = ProtobufCppRecipe()
