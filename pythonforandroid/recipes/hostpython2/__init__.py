
from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
from os.path import join, exists
from os import chdir, environ
import pythonforandroid.sh as sh
from pythonforandroid.patching import is_msys
from pythonforandroid.recipe import mpath

from distutils.dir_util import copy_tree


class Hostpython2Recipe(Recipe):
    version = "2.7.12" if is_msys() else "2.7.2"
    url = ('http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
           if not is_msys() else None)
    name = 'hostpython2'

    conflicts = ['hostpython3']

    mingw_package_prefix = 'mingw-w64-x86_64'
    mingw_prefix = 'mingw64'

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        return join(self.get_build_container_dir(), self.name)

    def prebuild_arch(self, arch):
        if not exists(self.get_build_dir()):
            shprint(sh.mkdir, '-p', self.get_build_dir())
        if not is_msys():
             # Override hostpython Setup?
             shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                     join(self.get_build_dir(), 'Modules', 'Setup'))

    def build_msys(self, arch):
        env = arch.msys_get_base_env(full=True, convert=True)
        if self.mingw_prefix.upper() != env['MSYSTEM']:
            raise Exception(
                "Msys system \"{}\" doesn't match the requested mingw version \"{}\"".
                format(env['MSYSTEM'], self.mingw_prefix.upper()))

        env['MINGW_PACKAGE_PREFIX'] = self.mingw_package_prefix
        env['CHERE_INVOKING'] = '1'
        build = self.get_build_dir()
        if 'PY4A_BUILD_TEMPDIR' in environ:
            tmp = shprint(sh.mktemp, '-d', '-p', mpath(environ['PY4A_BUILD_TEMPDIR']),
                          _env=env).stdout.strip()
        else:
            tmp = build

        root = join(tmp, 'mingw_{}'.format(self.version))

        shprint(sh.cp, '-r', join(self.get_recipe_dir(), 'mingw_{}'.format(self.version)), tmp)
        shprint(sh.bash, '-c', 'makepkg', _env=env, _cwd=root)
        shprint(sh.mv, mpath(join(root, 'pkg', '{}-python2'.format(self.mingw_package_prefix),
            self.mingw_prefix, '*')), tmp)
        shprint(sh.mv, join(root, 'src'), join(root, 'src_original'))

        if tmp != root:
            copy_tree(tmp, build)
            shprint(sh.rm, '-rf', tmp)

    def build_arch(self, arch):
        base_ver = self.version.rsplit('.', 1)[0]
        with current_directory(self.get_build_dir()):

            if exists('hostpython'):
                info('hostpython already exists, skipping build')
                self.ctx.hostpython = join(self.get_build_dir(),
                                           'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir(),
                                           'hostpgen')
                self.ctx.shared_lib = join(self.get_build_dir(), 'libpython{}.dll'.format(base_ver))
                if not exists(self.ctx.shared_lib):
                    self.ctx.shared_lib = ''
                return

            if is_msys():
                self.build_msys(arch)
            else:
                configure = sh.Command('./configure')
                shprint(configure)
                shprint(sh.make, '-j5')

            shprint(sh.mv, join('Parser', 'pgen'), 'hostpgen')
            if exists('hostpgen.exe'):
                shprint(sh.mv, 'hostpgen.exe', 'hostpgen')

            if exists('python.exe'):
                shprint(sh.mv, 'python.exe', 'hostpython')
            elif exists('python'):
                shprint(sh.mv, 'python', 'hostpython')
            else:
                warning('Unable to find the python executable after '
                        'hostpython build! Exiting.')
                exit(1)

        self.ctx.hostpython = join(self.get_build_dir(), 'hostpython')
        self.ctx.hostpgen = join(self.get_build_dir(), 'hostpgen')
        self.ctx.shared_lib = join(self.get_build_dir(), 'libpython{}.dll'.format(base_ver))
        if not exists(self.ctx.shared_lib):
            self.ctx.shared_lib = ''


recipe = Hostpython2Recipe()
