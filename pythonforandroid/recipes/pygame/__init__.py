
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import debug, shprint, info, warning
from os.path import join
import sh
import glob


class PygameRecipe(Recipe):
    name = 'pygame'
    version = '1.9.1'
    url = 'http://pygame.org/ftp/pygame-{version}release.tar.gz'

    depends = ['python2legacy', 'sdl']
    conflicts = ['sdl2']

    patches = ['patches/fix-surface-access.patch',
               'patches/fix-array-surface.patch',
               'patches/fix-sdl-spam-log.patch']

    def get_recipe_env(self, arch=None):
        env = super(PygameRecipe, self).get_recipe_env(arch)
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform

        # Every recipe uses its own liblink path, object files are collected and biglinked later
        liblink_path = join(self.get_build_container_dir(arch.arch), 'objects_{}'.format(self.name))
        env['LIBLINK_PATH'] = liblink_path
        ensure_dir(liblink_path)
        return env

    def prebuild_arch(self, arch):
        if self.is_patched(arch):
            return
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_build_dir(arch.arch), 'Setup'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/png -I{jni_path}/jpeg'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl/include -I{jni_path}/sdl_mixer'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl_ttf -I{jni_path}/sdl_image'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        debug('pygame cflags', env['CFLAGS'])

        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{libs_path} -L{src_path}/obj/local/{arch} -lm -lz'.format(
            libs_path=self.ctx.libs_dir, src_path=self.ctx.bootstrap.build_dir, arch=env['ARCH'])

        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')

        with current_directory(self.get_build_dir(arch.arch)):
            info('hostpython is ' + self.ctx.hostpython)
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env,
                    _tail=10, _critical=True)

            info('strip is ' + env['STRIP'])
            build_lib = glob.glob('./build/lib*')
            assert len(build_lib) == 1
            print('stripping pygame')
            shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                    env['STRIP'], '{}', ';')

        warning('Should remove pygame tests etc. here, but skipping for now')


recipe = PygameRecipe()
