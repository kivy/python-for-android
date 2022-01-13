import sh
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import join
from multiprocessing import cpu_count


class LibcurlRecipe(Recipe):
    version = '7.55.1'
    url = 'https://curl.haxx.se/download/curl-7.55.1.tar.gz'
    built_libraries = {'libcurl.so': 'dist/lib'}
    depends = ['openssl']

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        openssl_recipe = self.get_recipe('openssl', self.ctx)
        openssl_dir = openssl_recipe.get_build_dir(arch.arch)

        env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        env['LIBS'] = env.get('LIBS', '') + openssl_recipe.link_libs_flags()

        with current_directory(self.get_build_dir(arch.arch)):
            dst_dir = join(self.get_build_dir(arch.arch), 'dist')
            shprint(
                sh.Command('./configure'),
                '--host={}'.format(arch.command_prefix),
                '--enable-shared',
                '--with-ssl={}'.format(openssl_dir),
                '--prefix={}'.format(dst_dir),
                _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LibcurlRecipe()
