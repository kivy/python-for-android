import sh
from os.path import exists, join
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class LibffiRecipe(Recipe):
    name = 'libffi'
    version = 'v3.2.1'
    url = 'https://github.com/atgreen/libffi/archive/{version}.zip'

    patches = ['remove-version-info.patch']

    def get_host(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            host = None
            with open('Makefile') as f:
                for line in f:
                    if line.startswith('host = '):
                        host = line.strip()[7:]
                        break

            if not host or not exists(host):
                raise RuntimeError('failed to find build output! ({})'
                                   .format(host))

            return host

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch.arch), self.get_host(arch), '.libs')

    def should_build(self, arch):
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libffi.so'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            try:
                shprint(sh.Command('autoreconf -vif'), _env=env)
            except sh.CommandNotFound:
                shprint(sh.autoreconf, '-vif', _env=env)
            shprint(sh.Command('./configure'), '--host=' + arch.toolchain_prefix,
                    '--prefix=' + self.ctx.get_python_install_dir(),
                    '--enable-shared', _env=env)
            shprint(sh.make, '-j5', 'libffi.la', _env=env)

            # dlname = None
            # with open(join(host, 'libffi.la')) as f:
            # 	for line in f:
            # 		if line.startswith('dlname='):
            # 			dlname = line.strip()[8:-1]
            # 			break
            #
            # if not dlname or not exists(join(host, '.libs', dlname)):
            # 	raise RuntimeError('failed to locate shared object! ({})'
            # 	                   .format(dlname))

            # shprint(sh.sed, '-i', 's/^dlname=.*$/dlname=\'libffi.so\'/', join(host, 'libffi.la'))

            self.install_libs(arch, join(self.get_host(arch), '.libs', 'libffi.so'))

    def get_include_dirs(self, arch):
        return [join(self.get_build_dir(arch.arch), self.get_host(arch), 'include')]


recipe = LibffiRecipe()
