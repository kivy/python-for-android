
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, info
from pythonforandroid.patching import will_build, check_any
import sh
from os.path import join


class PyjniusRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = [('python2', 'python3crystax'), ('sdl2', 'sdl', 'webviewjni'), 'six']
    site_packages_name = 'jnius'
    patches = [('sdl2_jnienv_getter.patch', will_build('sdl2')),
               ('webviewjni_jnienv_getter.patch', will_build('webviewjni'))]
    call_hostpython_via_targetpython = False

    def postbuild_arch(self, arch):
        super(PyjniusRecipe, self).postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)

    def get_recipe_env(self, arch=None):
        env = super(PyjniusRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        return env

recipe = PyjniusRecipe()
