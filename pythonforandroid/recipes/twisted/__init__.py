
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchAndroid, info, Recipe
from os.path import exists, join
import sh
import glob


class TwistedRecipe(CythonRecipe):
    # version = 'stable'
    version = '15.2'
    url = 'http://twistedmatrix.com/Releases/Twisted/{version}/Twisted-{version}.1.tar.bz2'

    depends = ['zope']

    def prebuild_arch(self, arch):
        super(TwistedRecipe, self).prebuild_arch(arch)

        # Need to whitelist tty.pyo and termios.so here

    def get_recipe_env(self, arch):
        env = super(TwistedRecipe, self).get_recipe_env(arch)
        env['PYTHONPATH'] = ':'.join([self.ctx.get_site_packages_dir()])
        print('env is', env)
        return env

    def build_cython_components(self, arch):
        info('Cythonizing anything necessary in {}'.format(self.name))
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            info('Trying first build of {} to get cython files: this is '
                 'expected to fail'.format(self.name))
            try:
                shprint(hostpython, 'setup.py', 'build_ext', _env=env)
            except sh.ErrorReturnCode_1:
                print()
                info('{} first build failed (as expected)'.format(self.name))

            info('Running cython where appropriate')
            shprint(sh.find, self.get_build_dir('armeabi'), '-iname', '*.pyx', '-exec',
                    self.ctx.cython, '{}', ';', _env=env)
            info('ran cython')

            # shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)

            print('stripping')
            build_lib = glob.glob('./build/lib*')
            shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                    env['STRIP'], '{}', ';', _env=env)
            print('stripped!?')
            # exit(1)

            # Here we do *not* use the normal hostpython binary in the
            # target python dir, because twisted tries to import
            # _io.so which would fail.
            hostpython_build = sh.Command(join(
                Recipe.get_recipe('hostpython2', self.ctx).get_build_dir('armeabi'),
                'hostpython'))
            shprint(hostpython_build, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir()),
                    '--install-lib=/lib/python2.7/site-packages', _env=env)


    def postbuild_arch(self, arch):
                sup

recipe = TwistedRecipe()
