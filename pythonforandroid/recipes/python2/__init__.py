from os.path import join, exists
from pythonforandroid.recipe import Recipe
from pythonforandroid.python import GuestPythonRecipe
from pythonforandroid.logger import shprint
import sh


class Python2Recipe(GuestPythonRecipe):
    '''
    The python2's recipe.

    .. note:: This recipe can be built only against API 21+

    .. versionchanged:: 0.6.0
        Updated to version 2.7.15 and the build process has been changed in
        favour of the recently added class
        :class:`~pythonforandroid.python.GuestPythonRecipe`
    '''
    version = "2.7.15"
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python2'

    depends = ['hostpython2']
    conflicts = ['python3crystax', 'python3', 'python2legacy']

    patches = [
               # new 2.7.15 patches
               # ('patches/fix-api-minor-than-21.patch',
               #  is_api_lt(21)), # Todo: this should be tested
               'patches/fix-missing-extensions.patch',
               'patches/fix-filesystem-default-encoding.patch',
               'patches/fix-gethostbyaddr.patch',
               'patches/fix-posix-declarations.patch',
               'patches/fix-pwd-gecos.patch']

    configure_args = ('--host={android_host}',
                      '--build={android_build}',
                      '--enable-shared',
                      '--disable-ipv6',
                      '--disable-toolbox-glue',
                      '--disable-framework',
                      'ac_cv_file__dev_ptmx=yes',
                      'ac_cv_file__dev_ptc=no',
                      '--without-ensurepip',
                      'ac_cv_little_endian_double=yes',
                      'ac_cv_header_langinfo_h=no',
                      '--prefix={prefix}',
                      '--exec-prefix={exec_prefix}')

    compiled_extension = '.pyo'

    def prebuild_arch(self, arch):
        super(Python2Recipe, self).prebuild_arch(arch)
        patch_mark = join(self.get_build_dir(arch.arch), '.openssl-patched')
        if 'openssl' in self.ctx.recipe_build_order and not exists(patch_mark):
            self.apply_patch(join('patches', 'enable-openssl.patch'), arch.arch)
            shprint(sh.touch, patch_mark)

    def set_libs_flags(self, env, arch):
        env = super(Python2Recipe, self).set_libs_flags(env, arch)
        if 'libffi' in self.ctx.recipe_build_order:
            # For python2 we need to tell configure that we want to use our
            # compiled libffi, this step is not necessary for python3.
            self.configure_args += ('--with-system-ffi',)

        if 'openssl' in self.ctx.recipe_build_order:
            recipe = Recipe.get_recipe('openssl', self.ctx)
            openssl_build = recipe.get_build_dir(arch.arch)
            env['OPENSSL_BUILD'] = openssl_build
            env['OPENSSL_VERSION'] = recipe.version
        return env


recipe = Python2Recipe()
