from os.path import join

from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class PILRecipe(CompiledComponentsPythonRecipe):
	name = 'pil'
	version = '1.1.7'
	url = 'http://effbot.org/downloads/Imaging-{version}.tar.gz'
	depends = ['python2', 'png', 'jpeg']
	site_packages_name = 'PIL'

	patches = ['disable-tk.patch',
	           'fix-directories.patch']

	def get_recipe_env(self, arch=None):
		env = super(PILRecipe, self).get_recipe_env(arch)

		png = self.get_recipe('png', self.ctx)
		png_lib_dir = png.get_lib_dir(arch)
		png_jni_dir = png.get_jni_dir(arch)
		jpeg = self.get_recipe('jpeg', self.ctx)
		jpeg_lib_dir = jpeg.get_lib_dir(arch)
		jpeg_jni_dir = jpeg.get_jni_dir(arch)
		env['JPEG_ROOT'] = '{}|{}'.format(jpeg_lib_dir, jpeg_jni_dir)

		cflags = ' -I{} -L{} -I{} -L{}'.format(png_jni_dir, png_lib_dir, jpeg_jni_dir, jpeg_lib_dir)
		env['CFLAGS'] += cflags
		env['CXXFLAGS'] += cflags
		env['CC'] += cflags
		env['CXX'] += cflags

		ndk_dir = self.ctx.ndk_platform
		ndk_lib_dir = join(ndk_dir, 'usr', 'lib')
		ndk_include_dir = join(ndk_dir, 'usr', 'include')
		env['ZLIB_ROOT'] = '{}|{}'.format(ndk_lib_dir, ndk_include_dir)

		return env


recipe = PILRecipe()
