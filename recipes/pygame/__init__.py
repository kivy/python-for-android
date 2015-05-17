
from toolchain import PythonRecipe, shprint, ArchAndroid, current_directory
from os.path import exists, join
import sh

class PygameRecipe(PythonRecipe):
    name = 'pygame'
    version = '1.9.1'
    url = 'http://pygame.org/ftp/pygame-{version}release.tar.gz'
    depends = ['python2', 'sdl']

    def prebuild_armeabi(self):
        if exists(join(self.get_build_dir('armeabi'), '.patched')):
            print('Pygame already patched, skipping.')
            return
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_actual_build_dir('armeabi'), 'Setup'))
        self.apply_patch(join('patches', 'fix-surface-access.patch'))
        self.apply_patch(join('patches', 'fix-array-surface.patch'))
        shprint(sh.touch, join(self.get_build_dir('armeabi'), '.patched'))
        
    def build_armeabi(self):
        # AND: I'm going to ignore any extra pythonrecipe or cythonrecipe behaviour for now
        
        env = ArchAndroid(self.ctx).get_env()
        
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/png -I{jni_path}/jpeg'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl/include -I{jni_path}/sdl_mixer'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl_ttf -I{jni_path}/sdl_image'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        print('pygame cflags', env['CFLAGS'])

        
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{libs_path} -L{src_path}/obj/local/{arch} -lm -lz'.format(
            libs_path=self.ctx.libs_dir, src_path=self.ctx.bootstrap.build_dir, arch=env['ARCH'])
        print('pygame ldflags', env['LDFLAGS'])

        env['LDSHARED'] = env['LIBLINK']

        with current_directory(self.get_actual_build_dir('armeabi')):
            print('hostpython is', self.ctx.hostpython)
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

            print('strip is', env['STRIP'])
            exit(1)


recipe = PygameRecipe()
