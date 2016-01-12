from os.path import dirname, join

from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CryptographyRecipe(CompiledComponentsPythonRecipe):
	name = 'cryptography'
	version = '1.1.2'
	url = 'https://pypi.python.org/packages/source/c/cryptography/cryptography-{version}.tar.gz'

	depends = [('python2', 'python3'), 'cffi', 'enum34', 'openssl', 'ipaddress', 'idna']

	patches = ['fix-cffi-path.patch',
	           'link-static.patch']

	# call_hostpython_via_targetpython = False

	def get_recipe_env(self, arch=None):
		env = super(CryptographyRecipe, self).get_recipe_env(arch)
	# 	# libffi = self.get_recipe('libffi', self.ctx)
	# 	# includes = libffi.get_include_dirs(arch)
	# 	# env['CFLAGS'] = ' -I'.join([env.get('CFLAGS', '')] + includes)
	# 	# env['LDFLAGS'] = (env.get('CFLAGS', '') + ' -L' +
	# 	#                   self.ctx.get_libs_dir(arch.arch))
		openssl = self.get_recipe('openssl', self.ctx)
		openssl_dir = openssl.get_build_dir(arch.arch)
		env['CFLAGS'] = env.get('CFLAGS', '') + ' -I' + join(openssl_dir, 'include')
		# env['LDFLAGS'] = env.get('LDFLAGS', '') + ' -L' + openssl.get_build_dir(arch.arch)
		env['LIBSSL'] = join(openssl_dir, 'libssl.a')
		env['LIBCRYPTO'] = join(openssl_dir, 'libcrypto.a')
		env['PYTHONPATH'] = ':'.join([
			join(dirname(self.real_hostpython_location), 'Lib'),
			join(dirname(self.real_hostpython_location), 'Lib', 'site-packages'),
			env['BUILDLIB_PATH'],
		])
		print env
		return env


recipe = CryptographyRecipe()
