from os.path import exists, join
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info, shprint
from pythonforandroid.util import current_directory
from glob import glob
import sh


class LibffiRecipe(Recipe):
    """
    Requires additional system dependencies on Ubuntu:
        - `automake` for the `aclocal` binary
        - `autoconf` for the `autoreconf` binary
        - `libltdl-dev` which defines the `LT_SYS_SYMBOL_USCORE` macro
    """
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

    def should_build(self, arch):
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libffi.so'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            shprint(sh.Command('./configure'),
                    '--host=' + arch.command_prefix,
                    '--prefix=' + self.ctx.get_python_install_dir(),
                    '--enable-shared', _env=env)
            # '--with-sysroot={}'.format(self.ctx.ndk_platform),
            # '--target={}'.format(arch.toolchain_prefix),

            # ndk 15 introduces unified headers required --sysroot and
            # -isysroot for libraries and headers. libtool's head explodes
            # trying to weave them into it's own magic. The result is a link
            # failure trying to link libc. We call make to compile the bits
            # and manually link...

            try:
                shprint(sh.make, '-j5', 'libffi.la', _env=env)
            except sh.ErrorReturnCode_2:
                info("make libffi.la failed as expected")
            cc = sh.Command(env['CC'].split()[0])
            cflags = env['CC'].split()[1:]
            host_build = join(self.get_build_dir(arch.arch), self.get_host(arch))

            arch_flags = ''
            if '-march=' in env['CFLAGS']:
                arch_flags = '-march={}'.format(env['CFLAGS'].split('-march=')[1])

            src_arch = arch.command_prefix.split('-')[0]
            if src_arch == 'x86_64':
                # libffi has not specific arch files for x86_64...so...using
                # the ones from x86 which seems to build fine...
                src_arch = 'x86'

            cflags.extend(arch_flags.split())
            cflags.extend(['-shared', '-fPIC', '-DPIC'])
            cflags.extend(glob(join(host_build, 'src/.libs/*.o')))
            cflags.extend(glob(join(host_build, 'src', src_arch, '.libs/*.o')))

            ldflags = env['LDFLAGS'].split()
            cflags.extend(ldflags)
            cflags.extend(['-Wl,-soname', '-Wl,libffi.so', '-o',
                           '.libs/libffi.so'])

            with current_directory(host_build):
                shprint(cc, *cflags, _env=env)

            shprint(sh.cp, '-t', self.ctx.get_libs_dir(arch.arch),
                    join(host_build, '.libs', 'libffi.so'))

    def get_include_dirs(self, arch):
        return [join(self.get_build_dir(arch.arch), self.get_host(arch),
                     'include')]


recipe = LibffiRecipe()
