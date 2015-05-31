
from toolchain import CythonRecipe, shprint, ArchAndroid, current_directory, info
import sh
import glob
from os.path import join, exists


class PyjniusRecipe(CythonRecipe):
    version  = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    depends = ['python2']
    site_packages_name = 'jnius'

    def postbuild_arch(self, arch):
        super(PyjniusRecipe, self).postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)

    # def build_armeabi(self):
    #     env = ArchAndroid(self.ctx).get_env()

    #     env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(self.ctx.libs_dir)
    #     env['LDSHARED'] = env['LIBLINK']

    #     # AND: Hack to make pyjnius setup.py detect android build
    #     env['NDKPLATFORM'] = 'NOTNONE'


    #     # AND: Don't forget to add a check whether pyjnius has already
    #     # been compiled. Currently it redoes it every time.
    #     # AND: This check can be for jnius in site packages

    #     with current_directory(self.get_build_dir('armeabi')):
    #         if exists('.done'):
    #             print('android module already compiled, exiting')
    #             return

    #         hostpython = sh.Command(self.ctx.hostpython)

    #         # First build is fake in order to generate files that will be cythonized
    #         print('First build attempt will fail as hostpython doesn\'t have cython available:')
    #         try:
    #             shprint(hostpython, 'setup.py', 'build_ext', _env=env)
    #         except sh.ErrorReturnCode_1:
    #             print('failed (as expected)')


    #         print('Running cython where appropriate')
    #         shprint(sh.find, self.get_build_dir('armeabi'), '-iname', '*.pyx', '-exec',
    #                 self.ctx.cython, '{}', ';', _env=env)
    #         print('ran cython')

    #         shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)


    #         print('stripping')
    #         build_lib = glob.glob('./build/lib*')
    #         shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
    #                 env['STRIP'], '{}', ';', _env=env)
    #         print('stripped!?')
    #         # exit(1)

    #         shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

    #         shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)

    #         sh.touch('.done')
            


recipe = PyjniusRecipe()
