from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join


class MysqldbRecipe(CompiledComponentsPythonRecipe):
    name = 'mysqldb'
    version = '1.2.5'
    url = 'https://pypi.python.org/packages/source/M/MySQL-python/MySQL-python-{version}.zip'
    site_packages_name = 'MySQLdb'

    depends = ['setuptools', 'libmysqlclient']

    patches = ['override-mysql-config.patch',
               'disable-zip.patch']

    # call_hostpython_via_targetpython = False

    def convert_newlines(self, filename):
        print('converting newlines in {}'.format(filename))
        with open(filename, 'rb') as f:
            data = f.read()
        with open(filename, 'wb') as f:
            f.write(data.replace(b'\r\n', b'\n').replace(b'\r', b'\n'))

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        setupbase = join(self.get_build_dir(arch.arch), 'setup')
        self.convert_newlines(setupbase + '.py')
        self.convert_newlines(setupbase + '_posix.py')

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)

        hostpython = self.get_recipe('hostpython3', self.ctx)
        # TODO: fix hardcoded path
        env['PYTHONPATH'] = (join(hostpython.get_build_dir(arch.arch),
                                  'build', 'lib.linux-x86_64-2.7') +
                             ':' + env.get('PYTHONPATH', ''))

        libmysql = self.get_recipe('libmysqlclient', self.ctx)
        mydir = join(libmysql.get_build_dir(arch.arch), 'libmysqlclient')
        # env['CFLAGS'] += ' -I' + join(mydir, 'include')
        # env['LDFLAGS'] += ' -L' + join(mydir)
        libdir = self.ctx.get_libs_dir(arch.arch)
        env['MYSQL_libs'] = env['MYSQL_libs_r'] = '-L' + libdir + ' -lmysql'
        env['MYSQL_cflags'] = env['MYSQL_include'] = '-I' + join(mydir,
                                                                 'include')

        return env


recipe = MysqldbRecipe()
