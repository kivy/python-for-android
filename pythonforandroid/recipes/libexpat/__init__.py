
import sh
from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
from multiprocessing import cpu_count


class LibexpatRecipe(Recipe):
    version = 'master'
    url = 'https://github.com/libexpat/libexpat/archive/{version}.zip'
    depends = []

    def should_build(self, arch):
        super(LibexpatRecipe, self).should_build(arch)
        return not exists(
            join(self.ctx.get_libs_dir(arch.arch), 'libexpat.so'))

    def build_arch(self, arch):
        super(LibexpatRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(join(self.get_build_dir(arch.arch), 'expat')):
            dst_dir = join(self.get_build_dir(arch.arch), 'dist')
            shprint(sh.Command('./buildconf.sh'), _env=env)
            shprint(
                sh.Command('./configure'),
                '--host=arm-linux-androideabi',
                '--enable-shared',
                '--without-xmlwf',
                '--prefix={}'.format(dst_dir),
                _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)
            shutil.copyfile(
                '{}/lib/libexpat.so'.format(dst_dir),
                join(self.ctx.get_libs_dir(arch.arch), 'libexpat.so'))


recipe = LibexpatRecipe()
