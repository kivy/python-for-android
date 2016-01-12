from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join


class MysqldbRecipe(CompiledComponentsPythonRecipe):
	name = 'mysqldb'
	version = '1.2.5'
	url = 'https://pypi.python.org/packages/source/M/MySQL-python/MySQL-python-{version}.zip'
	site_packages_name = 'MySQLdb'

	depends = ['python2', 'setuptools', 'libmysqlclient']

	patches = ['override-mysql-config.patch',
	           'disable-zip.patch']

	# call_hostpython_via_targetpython = False

	def get_recipe_env(self, arch=None):
		env = super(MysqldbRecipe, self).get_recipe_env(arch)

		hostpython = self.get_recipe('hostpython2', self.ctx)
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
