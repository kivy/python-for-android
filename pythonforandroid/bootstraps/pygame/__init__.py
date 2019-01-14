from pythonforandroid.toolchain import Bootstrap, current_directory, info, info_main, shprint
from pythonforandroid.util import ensure_dir
from os.path import join, exists
import sh


class PygameBootstrap(Bootstrap):
    name = 'pygame'

    recipe_depends = ['hostpython2legacy', 'python2legacy', 'pyjnius',
                      'sdl', 'pygame', 'android', 'kivy']

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

            python_bundle_dir = join('_python_bundle', '_python_bundle')
            if 'python2legacy' in self.ctx.recipe_build_order:
                # a special case with its own packaging location
                python_bundle_dir = 'private'
                # And also must had an install directory, make sure of that
                self.ctx.python_recipe.create_python_install(self.dist_dir)

            self.distribute_libs(
                arch, [join(self.build_dir, 'libs', arch.arch),
                       self.ctx.get_libs_dir(arch.arch)])
            self.distribute_aars(arch)
            self.distribute_javaclasses(self.ctx.javaclass_dir)

            ensure_dir(python_bundle_dir)
            site_packages_dir = self.ctx.python_recipe.create_python_bundle(
                join(self.dist_dir, python_bundle_dir), arch)

            if 'sqlite3' not in self.ctx.recipe_build_order:
                with open('blacklist.txt', 'a') as fileh:
                    fileh.write('\nsqlite3/*\nlib-dynload/_sqlite3.so\n')

        self.strip_libraries(arch)
        self.fry_eggs(site_packages_dir)
        super(PygameBootstrap, self).run_distribute()


bootstrap = PygameBootstrap()
