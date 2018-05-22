import sh
from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
from multiprocessing import cpu_count


class LibcurlRecipe(Recipe):
    version = '7.55.1'
    url = 'https://curl.haxx.se/download/curl-7.55.1.tar.gz'
    depends = ['openssl']

    def should_build(self, arch):
        super(LibcurlRecipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libcurl.so'))

    def build_arch(self, arch):
        super(LibcurlRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)

        r = self.get_recipe('openssl', self.ctx)
        openssl_dir = r.get_build_dir(arch.arch)

        with current_directory(self.get_build_dir(arch.arch)):
            dst_dir = join(self.get_build_dir(arch.arch), 'dist')
            shprint(
                sh.Command('./configure'),
                '--host=arm-linux-androideabi',
                '--enable-shared',
                '--with-ssl={}'.format(openssl_dir),
                '--prefix={}'.format(dst_dir),
                _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)
            shutil.copyfile('{}/lib/libcurl.so'.format(dst_dir),
                            join(
                                self.ctx.get_libs_dir(arch.arch),
                                'libcurl.so'))


recipe = LibcurlRecipe()
