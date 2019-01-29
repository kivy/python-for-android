from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from pythonforandroid.util import ensure_dir
from os.path import exists, join
import sh


class LibZMQRecipe(Recipe):
    version = '4.1.4'
    url = 'http://download.zeromq.org/zeromq-{version}.tar.gz'
    depends = []

    def should_build(self, arch):
        super(LibZMQRecipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libzmq.so'))

    def build_arch(self, arch):
        super(LibZMQRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        #
        # libsodium_recipe = Recipe.get_recipe('libsodium', self.ctx)
        # libsodium_dir = libsodium_recipe.get_build_dir(arch.arch)
        # env['sodium_CFLAGS'] = '-I{}'.format(join(
        #     libsodium_dir, 'src'))
        # env['sodium_LDLAGS'] = '-L{}'.format(join(
        #     libsodium_dir, 'src', 'libsodium', '.libs'))

        curdir = self.get_build_dir(arch.arch)
        prefix = join(curdir, "install")
        with current_directory(curdir):
            bash = sh.Command('sh')
            shprint(
                bash, './configure',
                '--host=arm-linux-androideabi',
                '--without-documentation',
                '--prefix={}'.format(prefix),
                '--with-libsodium=no',
                _env=env)
            shprint(sh.make, _env=env)
            shprint(sh.make, 'install', _env=env)
            shutil.copyfile('.libs/libzmq.so', join(
                self.ctx.get_libs_dir(arch.arch), 'libzmq.so'))

            bootstrap_obj_dir = join(self.ctx.bootstrap.build_dir, 'obj', 'local', arch.arch)
            ensure_dir(bootstrap_obj_dir)
            shutil.copyfile(
                '{}/sources/cxx-stl/gnu-libstdc++/{}/libs/{}/libgnustl_shared.so'.format(
                    self.ctx.ndk_dir, self.ctx.toolchain_version, arch),
                join(bootstrap_obj_dir, 'libgnustl_shared.so'))

            # Copy libgnustl_shared.so
            with current_directory(self.get_build_dir(arch.arch)):
                sh.cp(
                    "{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/libs/{arch.arch}/libgnustl_shared.so".format(ctx=self.ctx, arch=arch),
                    self.ctx.get_libs_dir(arch.arch)
                )

    def get_recipe_env(self, arch):
        # XXX should stl be configuration for the toolchain itself?
        env = super(LibZMQRecipe, self).get_recipe_env(arch)
        env['CFLAGS'] += ' -Os'
        env['CXXFLAGS'] += ' -Os -fPIC -fvisibility=default'
        env['CXXFLAGS'] += ' -I{}/sources/cxx-stl/gnu-libstdc++/{}/include'.format(
            self.ctx.ndk_dir, self.ctx.toolchain_version)
        env['CXXFLAGS'] += ' -I{}/sources/cxx-stl/gnu-libstdc++/{}/libs/{}/include'.format(
            self.ctx.ndk_dir, self.ctx.toolchain_version, arch)
        env['CXXFLAGS'] += ' -L{}/sources/cxx-stl/gnu-libstdc++/{}/libs/{}'.format(
            self.ctx.ndk_dir, self.ctx.toolchain_version, arch)
        env['CXXFLAGS'] += ' -lgnustl_shared'
        env['LDFLAGS'] += ' -L{}/sources/cxx-stl/gnu-libstdc++/{}/libs/{}'.format(
            self.ctx.ndk_dir, self.ctx.toolchain_version, arch)
        return env


recipe = LibZMQRecipe()
