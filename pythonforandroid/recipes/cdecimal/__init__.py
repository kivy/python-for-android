
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe
from pythonforandroid.patching import is_darwin


class CdecimalRecipe(CompiledComponentsPythonRecipe):
    name = 'cdecimal'
    version = '2.3'
    url = 'http://www.bytereef.org/software/mpdecimal/releases/cdecimal-{version}.tar.gz'

    depends = ['python2']

    patches = ['locale.patch',
               'cross-compile.patch']

    def prebuild_arch(self, arch):
        super(CdecimalRecipe, self).prebuild_arch(arch)
        if not is_darwin():
            self.setup_extra_args = ['--with-machine=ansi32']


recipe = CdecimalRecipe()
