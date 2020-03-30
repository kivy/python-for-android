from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.patching import is_darwin


class CdecimalRecipe(CompiledComponentsPythonRecipe):
    name = 'cdecimal'
    version = '2.3'
    url = 'http://www.bytereef.org/software/mpdecimal/releases/cdecimal-{version}.tar.gz'

    depends = []

    patches = ['locale.patch',
               'cross-compile.patch']

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        if not is_darwin():
            if '64' in arch.arch:
                machine = 'ansi64'
            else:
                machine = 'ansi32'
            self.setup_extra_args = ['--with-machine=' + machine]


recipe = CdecimalRecipe()
