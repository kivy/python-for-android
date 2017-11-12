from pythonforandroid.toolchain import Bootstrap, shprint, current_directory, info, warning, ArchARM, info_main
from os.path import join, exists
from os import walk
import glob
import sh


class PygameBootstrap(Bootstrap):
    name = 'pygame'

    recipe_depends = ['hostpython2', 'python2', 'pyjnius', 'sdl', 'pygame',
                      'android', 'kivy']

    def run_distribute(self):
        info_main('# Creating Android project from build and {} bootstrap'.format(
            self.name))

        # src_path = join(self.ctx.root_dir, 'bootstrap_templates',
        #                 self.name)
        src_path = join(self.bootstrap_dir, 'build')

        arch = self.ctx.archs[0]
        if len(self.ctx.archs) > 1:
            raise ValueError('built for more than one arch, but bootstrap cannot handle that yet')
        info('Bootstrap running with arch {}'.format(arch))

        with current_directory(self.dist_dir):

            info('Creating initial layout')
            for dirname in ('assets', 'bin', 'private', 'res', 'templates'):
                if not exists(dirname):
                    shprint(sh.mkdir, dirname)

            info('Copying default files')
            shprint(sh.cp, '-a', join(self.build_dir, 'project.properties'), '.')
            shprint(sh.cp, '-a', join(src_path, 'build.py'), '.')
            shprint(sh.cp, '-a', join(src_path, 'buildlib'), '.')
            shprint(sh.cp, '-a', join(src_path, 'src'), '.')
            shprint(sh.cp, '-a', join(src_path, 'templates'), '.')
            shprint(sh.cp, '-a', join(src_path, 'res'), '.')
            shprint(sh.cp, '-a', join(src_path, 'blacklist.txt'), '.')
            shprint(sh.cp, '-a', join(src_path, 'whitelist.txt'), '.')

            with open('local.properties', 'w') as fileh:
                fileh.write('sdk.dir={}'.format(self.ctx.sdk_dir))

            info('Copying python distribution')
            hostpython = sh.Command(self.ctx.hostpython)
            try:
                shprint(hostpython, '-OO', '-m', 'compileall', self.ctx.get_python_install_dir(),
                        _tail=10, _filterout="^Listing")
            except sh.ErrorReturnCode:
                pass
            if not exists('python-install'):
                shprint(sh.cp, '-a', self.ctx.get_python_install_dir(), './python-install')

            self.distribute_libs(arch, [join(self.build_dir, 'libs', arch.arch), self.ctx.get_libs_dir(arch.arch)]);
            self.distribute_aars(arch)
            self.distribute_javaclasses(self.ctx.javaclass_dir)

            info('Filling private directory')
            if not exists(join('private', 'lib')):
                shprint(sh.cp, '-a', join('python-install', 'lib'), 'private')
            shprint(sh.mkdir, '-p', join('private', 'include', 'python2.7'))

            shprint(sh.mv, join('libs', arch.arch, 'libpymodules.so'), 'private/')
            shprint(sh.cp, join('python-install', 'include' , 'python2.7', 'pyconfig.h'), join('private', 'include', 'python2.7/'))

            info('Removing some unwanted files')
            shprint(sh.rm, '-f', join('private', 'lib', 'libpython2.7.so'))
            shprint(sh.rm, '-rf', join('private', 'lib', 'pkgconfig'))

            with current_directory(join(self.dist_dir, 'private', 'lib', 'python2.7')):
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
                shprint(sh.rm, '-rf', 'lib-dynload/_ctypes_test.so')
                shprint(sh.rm, '-rf', 'lib-dynload/_testcapi.so')


        self.strip_libraries(arch)
        super(PygameBootstrap, self).run_distribute()

bootstrap = PygameBootstrap()
