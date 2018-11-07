
from pythonforandroid.recipe import TargetPythonRecipe
from pythonforandroid.toolchain import shprint
from pythonforandroid.logger import info, error
from pythonforandroid.util import ensure_dir, temp_directory
from os.path import exists, join
import sh

prebuilt_download_locations = {
    '3.6': ('https://github.com/inclement/crystax_python_builds/'
            'releases/download/0.1/crystax_python_3.6_armeabi_armeabi-v7a.tar.gz')}


class Python3CrystaXRecipe(TargetPythonRecipe):
    version = '3.6'
    url = ''
    name = 'python3crystax'

    depends = ['hostpython3crystax']
    conflicts = ['python2', 'python3']

    from_crystax = True

    def get_dir_name(self):
        name = super(Python3CrystaXRecipe, self).get_dir_name()
        name += '-version{}'.format(self.version)
        return name

    def build_arch(self, arch):
        # We don't have to actually build anything as CrystaX comes
        # with the necessary modules. They are included by modifying
        # the Android.mk in the jni folder.

        # If the Python version to be used is not prebuilt with the CrystaX
        # NDK, we do have to download it.

        crystax_python_dir = join(self.ctx.ndk_dir, 'sources', 'python')
        if not exists(join(crystax_python_dir, self.version)):
            info(('The NDK does not have a prebuilt Python {}, trying '
                  'to obtain one.').format(self.version))

            if self.version not in prebuilt_download_locations:
                error(('No prebuilt version for Python {} could be found, '
                       'the built cannot continue.'))
                exit(1)

            with temp_directory() as td:
                self.download_file(prebuilt_download_locations[self.version],
                                   join(td, 'downloaded_python'))
                shprint(sh.tar, 'xf', join(td, 'downloaded_python'),
                        '--directory', crystax_python_dir)

            if not exists(join(crystax_python_dir, self.version)):
                error(('Something went wrong, the directory at {} should '
                       'have been created but does not exist.').format(
                           join(crystax_python_dir, self.version)))

        if not exists(join(
                crystax_python_dir, self.version, 'libs', arch.arch)):
            error(('The prebuilt Python for version {} does not contain '
                   'binaries for your chosen architecture "{}".').format(
                       self.version, arch.arch))
            exit(1)

        # TODO: We should have an option to build a new Python. This
        # would also allow linking to openssl and sqlite from CrystaX.

        dirn = self.ctx.get_python_install_dir()
        ensure_dir(dirn)

        # Instead of using a locally built hostpython, we use the
        # user's Python for now. They must have the right version
        # available. Using e.g. pyenv makes this easy.
        self.ctx.hostpython = 'python{}'.format(self.version)

    def create_python_bundle(self, dirn, arch):
        ndk_dir = self.ctx.ndk_dir
        py_recipe = self.ctx.python_recipe
        python_dir = join(ndk_dir, 'sources', 'python',
                          py_recipe.version, 'libs', arch.arch)
        shprint(sh.cp, '-r', join(python_dir,
                                  'stdlib.zip'), dirn)
        shprint(sh.cp, '-r', join(python_dir,
                                  'modules'), dirn)
        shprint(sh.cp, '-r', self.ctx.get_python_install_dir(),
                join(dirn, 'site-packages'))

        info('Renaming .so files to reflect cross-compile')
        self.reduce_object_file_names(join(dirn, "site-packages"))

        return join(dirn, 'site-packages')

    def include_root(self, arch_name):
        return join(self.ctx.ndk_dir, 'sources', 'python', self.major_minor_version_string,
                    'include', 'python')

    def link_root(self, arch_name):
        return join(self.ctx.ndk_dir, 'sources', 'python', self.major_minor_version_string,
                    'libs', arch_name)


recipe = Python3CrystaXRecipe()
