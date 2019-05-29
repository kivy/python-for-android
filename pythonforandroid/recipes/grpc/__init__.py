from os.path import join, isdir, isfile
import sh
from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import (
    current_directory,
    shprint,
)
from pythonforandroid.logger import info
from multiprocessing import cpu_count


class GRPCRecipe(NDKRecipe):
    version = 'v1.20.1'
    #url = 'https://github.com/grpc/grpc/archive/{version}.zip'
    url = None
    port_git = 'https://github.com/grpc/grpc.git'
    generated_libraries = [
        'libgrpc++_cronet.so',
        'libgrpc_csharp_ext.so',
        'libgrpc++_unsecure.so',
        'libgrpc_plugin_support.so',
        'libgrpc++.so',
        'libgrpc_cronet.so',
        'libgrpc_unsecure.so',
        'libgrpc.so',
        'libaddress_sorting.a',
        'libbenchmark.a',
        'libbenchmark_main.a',
        'libcares.so',
        'libcrypto.a',
        'libgflags.a',
        'libgflags_nothreads.a',
        'libglog.a',
        'libgpr.a',
        'libgrpc.a',
        'libgrpc++.a',
        'libgrpc_cronet.a',
        'libgrpc++_cronet.a',
        'libgrpc_csharp_ext.so',
        'libgrpc_plugin_support.a',
        'libgrpc_unsecure.a',
        'libgrpc++_unsecure.a',
        'libprotobuf.a',
        'libprotobuf-lite.a',
        'libprotoc.a',
        'libssl.a',
        'libz.a',
        'libz.so'
    ]

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'build', 'lib', arch.arch)

    def get_recipe_env(self, arch):
        env = super(GRPCRecipe, self).get_recipe_env(arch)
        env['ANDROID_NDK'] = self.ctx.ndk_dir
        env['ANDROID_SDK'] = self.ctx.sdk_dir
        return env

    def prebuild_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        source_dir = join(build_dir, 'grpc')
        if not isfile(join(source_dir, 'setup.py')):
            info("clone GRPC sources from {}".format(self.port_git))
            shprint(sh.git, 'clone', '--recursive', self.port_git, source_dir, _tail=20, _critical=True)

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        source_dir = join(build_dir, 'grpc')
        build_dir = join(source_dir, 'build')
        shprint(sh.rm, '-rf', build_dir)
        shprint(sh.mkdir, '-p', build_dir)
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)

            python_major = self.ctx.python_recipe.version[0]
            python_include_root = self.ctx.python_recipe.include_root(arch.arch)
            python_site_packages = self.ctx.get_site_packages_dir()
            python_link_root = self.ctx.python_recipe.link_root(arch.arch)
            python_link_version = self.ctx.python_recipe.major_minor_version_string
            if 'python3' in self.ctx.python_recipe.name:
                python_link_version += 'm'
            python_library = join(python_link_root,
                                  'libpython{}.so'.format(python_link_version))
            python_include_numpy = join(python_site_packages,
                                        'numpy', 'core', 'include')

            shprint(sh.cmake,
                    '-DP4A=ON',
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DANDROID_STANDALONE_TOOLCHAIN={}'.format(self.ctx.ndk_dir),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),
                    '-DANDROID_EXECUTABLE={}/tools/android'.format(env['ANDROID_SDK']),
                    '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                        join(self.ctx.ndk_dir, 'build', 'cmake',
                             'android.toolchain.cmake')),
                    '-DBUILD_WITH_STANDALONE_TOOLCHAIN=ON',
                    '-DBUILD_SHARED_LIBS=ON',
                    '-DBUILD_STATIC_LIBS=OFF',
                    '-Dprotobuf_BUILD_PROTOC_BINARIES=OFF',
                    '-DCMAKE_INSTALL_PREFIX="/opt/install"',
                    '-DCMAKE_FIND_ROOT_PATH="/opt/install"',
                    '-DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=BOTH',
                    '-DCMAKE_SHARED_LINKER_FLAGS="-llog"',
                    '-DCMAKE_EXE_LINKER_FLAGS="-llog"',
                    '-DProtobuf_PROTOC_EXECUTABLE=/usr/local/bin/protoc',
                    '-DProtobuf_LIBRARIES=/opt/install/lib/libprotobuf.a',
                    '-DProtobuf_PROTOC_LIBRARY=/opt/install/lib/libprotoc.a',
                    '-DProtobuf_INCLUDE_DIR=/opt/install/include',
                    '-DHAVE_THREAD_SAFETY_ATTRIBUTES=ON',
                    '-DHAVE_GNU_POSIX_REGEX=ON',
                    '-DHAVE_STD_REGEX=ON',
                    '-DRUN_HAVE_STD_REGEX=ON',
                    '-DHAVE_POSIX_REGEX=1',
                    '-DRUN_HAVE_POSIX_REGEX=ON',
                    '-DHAVE_STEADY_CLOCK=ON',
                    '-DgRPC_BUILD_TESTS=OFF',
                    '-DCMAKE_CROSSCOMPILING=1',
                    '-DOPENSSL_SSL_LIBRARY=/usr/local/lib/libssl.so',
                    '-DOPENSSL_CRYPTO_LIBRARY=/usr/local/lib/libcrypto.so',
                    '-DOPENSSL_INCLUDE_DIR=/usr/local/include',
                    '-Dgflags_DIR=/opt/install/lib/cmake/gflags',
                    '-DgRPC_PROTOBUF_PROVIDER=package',
                    '-DgRPC_ZLIB_PROVIDER=package',
                    '-DgRPC_CARES_PROVIDER=package',
                    '-DgRPC_SSL_PROVIDER=package',
                    '-DgRPC_GFLAGS_PROVIDER=package',
                    '-DgRPC_BUILD_CODEGEN=OFF',

                    source_dir,
                    _env=env)
            shprint(sh.make, '-j' + str(cpu_count()))
            # Copy third party shared libs that we need in our final apk
            #sh.cp('-a', sh.glob('./lib/{}/lib*.a'.format(arch.arch)),
            #      self.ctx.get_libs_dir(arch.arch))

             # copy static libs to libs collection
            for lib in sh.glob(join(build_dir, '*.a')):
                shprint(sh.cp, '-L', lib, self.ctx.libs_dir)

            for lib in sh.glob(join(build_dir, '*.so')):
                shprint(sh.cp, '-L', lib, self.ctx.libs_dir)


recipe = GRPCRecipe()
