from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CffiRecipe(CompiledComponentsPythonRecipe):
	name = 'cffi'
	version = '1.4.2'
	url = 'https://pypi.python.org/packages/source/c/cffi/cffi-{version}.tar.gz'

	depends = [('python2', 'python3'), 'setuptools', 'pycparser', 'libffi']

	patches = ['disable-pkg-config.patch']

	# call_hostpython_via_targetpython = False
	install_in_hostpython = True

	def get_recipe_env(self, arch=None):
		env = super(CffiRecipe, self).get_recipe_env(arch)
		libffi = self.get_recipe('libffi', self.ctx)
		includes = libffi.get_include_dirs(arch)
		env['CFLAGS'] = ' -I'.join([env.get('CFLAGS', '')] + includes)
		env['LDFLAGS'] = (env.get('CFLAGS', '') + ' -L' +
		                  self.ctx.get_libs_dir(arch.arch))
		env['PYTHONPATH'] = ':'.join([
			self.ctx.get_site_packages_dir(),
			env['BUILDLIB_PATH'],
		])
		return env


recipe = CffiRecipe()
