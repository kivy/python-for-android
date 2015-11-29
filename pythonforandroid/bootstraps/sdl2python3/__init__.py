from pythonforandroid.toolchain import Bootstrap, shprint, current_directory, info, warning, ArchARM, info_main
from os.path import join, exists
from os import walk
import glob
import sh

class SDL2Bootstrap(Bootstrap):
    name = 'sdl2python3'

    recipe_depends = ['sdl2python3', 'python3']

    can_be_chosen_automatically = False

    def run_distribute(self):
        info_main('# Creating Android project from build and {} bootstrap'.format(
            self.name))

        info('This currently just copies the SDL2 build stuff straight from the build dir.')
        shprint(sh.rm, '-rf', self.dist_dir)
        shprint(sh.cp, '-r', self.build_dir, self.dist_dir)
        with current_directory(self.dist_dir):
            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

        # AND: Hardcoding armeabi - naughty!
        arch = ArchARM(self.ctx)

        with current_directory(self.dist_dir):
            info('Copying python distribution')

            if not exists('private'):
                shprint(sh.mkdir, 'private')
            if not exists('assets'):
                shprint(sh.mkdir, 'assets')
            
            hostpython = sh.Command(self.ctx.hostpython)

            # AND: The compileall doesn't work with python3, tries to import a wrong-arch lib
            # shprint(hostpython, '-OO', '-m', 'compileall', join(self.ctx.build_dir, 'python-install'))
            if not exists('python-install'):
                shprint(sh.cp, '-a', join(self.ctx.build_dir, 'python-install'), '.')

            self.distribute_libs(arch, [self.ctx.libs_dir])
            self.distribute_aars(arch)
            self.distribute_javaclasses(join(self.ctx.build_dir, 'java'))

            info('Filling private directory')
            if not exists(join('private', 'lib')):
                info('private/lib does not exist, making')
                shprint(sh.cp, '-a', join('python-install', 'lib'), 'private')
            shprint(sh.mkdir, '-p', join('private', 'include', 'python3.4m'))
            
            # AND: Copylibs stuff should go here
            if exists(join('libs', 'armeabi', 'libpymodules.so')):
                shprint(sh.mv, join('libs', 'armeabi', 'libpymodules.so'), 'private/')
            shprint(sh.cp, join('python-install', 'include' , 'python3.4m', 'pyconfig.h'), join('private', 'include', 'python3.4m/'))

            info('Removing some unwanted files')
            shprint(sh.rm, '-f', join('private', 'lib', 'libpython3.4m.so'))
            shprint(sh.rm, '-f', join('private', 'lib', 'libpython3.so'))
            shprint(sh.rm, '-rf', join('private', 'lib', 'pkgconfig'))

            with current_directory(join(self.dist_dir, 'private', 'lib', 'python3.4')):
                # shprint(sh.xargs, 'rm', sh.grep('-E', '*\.(py|pyx|so\.o|so\.a|so\.libs)$', sh.find('.')))
                removes = []
                for dirname, something, filens in walk('.'):
                    for filename in filens:
                        for suffix in ('py', 'pyc', 'so.o', 'so.a', 'so.libs'):
                            if filename.endswith(suffix):
                                removes.append(filename)
                shprint(sh.rm, '-f', *removes)

                info('Deleting some other stuff not used on android')
                # To quote the original distribute.sh, 'well...'
                # shprint(sh.rm, '-rf', 'ctypes')
                shprint(sh.rm, '-rf', 'lib2to3')
                shprint(sh.rm, '-rf', 'idlelib')
                for filename in glob.glob('config/libpython*.a'):
                    shprint(sh.rm, '-f', filename)
                shprint(sh.rm, '-rf', 'config/python.o')
                # shprint(sh.rm, '-rf', 'lib-dynload/_ctypes_test.so')
                # shprint(sh.rm, '-rf', 'lib-dynload/_testcapi.so')


        self.strip_libraries(arch)
        super(SDL2Bootstrap, self).run_distribute()

bootstrap = SDL2Bootstrap()
