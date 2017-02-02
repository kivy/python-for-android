from pythonforandroid.toolchain import Bootstrap, shprint, current_directory, info, warning, ArchARM, info_main
from os.path import join, exists, curdir, abspath
from os import walk
import glob
import sh

class SDL2Bootstrap(Bootstrap):
    name = 'sdl2'

    recipe_depends = ['sdl2', ('python2', 'python3crystax')]

    def run_distribute(self):
        info_main('# Creating Android project from build and {} bootstrap'.format(
            self.name))

        info('This currently just copies the SDL2 build stuff straight from the build dir.')
        shprint(sh.rm, '-rf', self.dist_dir)
        shprint(sh.cp, '-r', self.build_dir, self.dist_dir)
        with current_directory(self.dist_dir):
            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

        arch = self.ctx.archs[0]
        if len(self.ctx.archs) > 1:
            raise ValueError('built for more than one arch, but bootstrap cannot handle that yet')
        info('Bootstrap running with arch {}'.format(arch))

        with current_directory(self.dist_dir):
            info('Copying python distribution')

            if not exists('private') and not self.ctx.python_recipe.from_crystax:
                shprint(sh.mkdir, 'private')
            if not exists('crystax_python') and self.ctx.python_recipe.from_crystax:
                shprint(sh.mkdir, 'crystax_python')
                shprint(sh.mkdir, 'crystax_python/crystax_python')
            if not exists('assets'):
                shprint(sh.mkdir, 'assets')

            hostpython = sh.Command(self.ctx.hostpython)
            if not self.ctx.python_recipe.from_crystax:
                try:
                    shprint(hostpython, '-OO', '-m', 'compileall',
                            self.ctx.get_python_install_dir(),
                            _tail=10, _filterout="^Listing")
                except sh.ErrorReturnCode:
                    pass
                if not exists('python-install'):
                    shprint(sh.cp, '-a', self.ctx.get_python_install_dir(), './python-install')

            self.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
            self.distribute_aars(arch)
            self.distribute_javaclasses(self.ctx.javaclass_dir)

            if not self.ctx.python_recipe.from_crystax:
                info('Filling private directory')
                if not exists(join('private', 'lib')):
                    info('private/lib does not exist, making')
                    shprint(sh.cp, '-a', join('python-install', 'lib'), 'private')
                shprint(sh.mkdir, '-p', join('private', 'include', 'python2.7'))

                # AND: Copylibs stuff should go here
                if exists(join('libs', arch.arch, 'libpymodules.so')):
                    shprint(sh.mv, join('libs', arch.arch, 'libpymodules.so'), 'private/')
                shprint(sh.cp, join('python-install', 'include' , 'python2.7', 'pyconfig.h'), join('private', 'include', 'python2.7/'))

                info('Removing some unwanted files')
                shprint(sh.rm, '-f', join('private', 'lib', 'libpython2.7.so'))
                shprint(sh.rm, '-rf', join('private', 'lib', 'pkgconfig'))

                libdir = join(self.dist_dir, 'private', 'lib', 'python2.7')
                site_packages_dir = join(libdir, 'site-packages')
                with current_directory(libdir):
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

            else:  # Python *is* loaded from crystax
                ndk_dir = self.ctx.ndk_dir
                py_recipe = self.ctx.python_recipe
                python_dir = join(ndk_dir, 'sources', 'python', py_recipe.version,
                                  'libs', arch.arch)

                shprint(sh.cp, '-r', join(python_dir, 'stdlib.zip'), 'crystax_python/crystax_python')
                shprint(sh.cp, '-r', join(python_dir, 'modules'), 'crystax_python/crystax_python')
                shprint(sh.cp, '-r', self.ctx.get_python_install_dir(), 'crystax_python/crystax_python/site-packages')

                info('Renaming .so files to reflect cross-compile')
                site_packages_dir = 'crystax_python/crystax_python/site-packages'
                filens = shprint(sh.find, site_packages_dir, '-iname', '*.so').stdout.decode(
                    'utf-8').split('\n')[:-1]
                for filen in filens:
                    parts = filen.split('.')
                    if len(parts) <= 2:
                        continue
                    shprint(sh.mv, filen, filen.split('.')[0] + '.so')
                site_packages_dir = join(abspath(curdir),
                                         site_packages_dir)
            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')


        self.strip_libraries(arch)
        self.fry_eggs(site_packages_dir)
        super(SDL2Bootstrap, self).run_distribute()

bootstrap = SDL2Bootstrap()
