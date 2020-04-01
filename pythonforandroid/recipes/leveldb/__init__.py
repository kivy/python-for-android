from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import join
import sh


class LevelDBRecipe(Recipe):
    version = '1.18'
    url = 'https://github.com/google/leveldb/archive/v{version}.tar.gz'
    opt_depends = ['snappy']
    patches = ['disable-so-version.patch', 'find-snappy.patch']

    def should_build(self, arch):
        return not self.has_libs(arch, 'libleveldb.so', 'libgnustl_shared.so')

    def build_arch(self, arch):
        super(LevelDBRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            if 'snappy' in recipe.ctx.recipe_build_order:
                # Copy source from snappy recipe
                sh.cp('-rf', self.get_recipe('snappy', self.ctx).get_build_dir(arch.arch), 'snappy')
            # Build
            shprint(sh.make, _env=env)
            # Copy the shared library
            shutil.copyfile('libleveldb.so', join(self.ctx.get_libs_dir(arch.arch), 'libleveldb.so'))
        # Copy stl
        shutil.copyfile(self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + '/libgnustl_shared.so',
                        join(self.ctx.get_libs_dir(arch.arch), 'libgnustl_shared.so'))

    def get_recipe_env(self, arch):
        env = super(LevelDBRecipe, self).get_recipe_env(arch)
        env['TARGET_OS'] = 'OS_ANDROID_CROSSCOMPILE'
        if 'snappy' in recipe.ctx.recipe_build_order:
            env['CFLAGS'] += ' -DSNAPPY' + \
                             ' -I./snappy'
        env['CFLAGS'] += ' -I' + self.ctx.ndk_dir + '/platforms/android-' + str(self.ctx.android_api) + '/arch-' + arch.arch.replace('eabi', '') + '/usr/include' + \
                         ' -I' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/include' + \
                         ' -I' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + '/include'
        env['CXXFLAGS'] = env['CFLAGS']
        env['CXXFLAGS'] += ' -frtti'
        env['CXXFLAGS'] += ' -fexceptions'
        env['LDFLAGS'] += ' -L' + self.ctx.ndk_dir + '/sources/cxx-stl/gnu-libstdc++/' + self.ctx.toolchain_version + '/libs/' + arch.arch + \
                          ' -lgnustl_shared'
        return env


recipe = LevelDBRecipe()
