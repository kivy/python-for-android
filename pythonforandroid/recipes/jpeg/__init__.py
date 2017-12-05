from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from os.path import join, exists
import sh


class JpegRecipe(NDKRecipe):
	name = 'jpeg'
	version = 'linaro-android'
	url = 'git://git.linaro.org/people/tomgall/libjpeg-turbo/libjpeg-turbo.git'

	patches = ['build-static.patch']

	generated_libraries = ['libjpeg.a']

	def prebuild_arch(self, arch):
		super(JpegRecipe, self).prebuild_arch(arch)

		build_dir = self.get_build_dir(arch.arch)
		app_mk = join(build_dir, 'Application.mk')
		if not exists(app_mk):
			shprint(sh.cp, join(self.get_recipe_dir(), 'Application.mk'), app_mk)
		jni_ln = join(build_dir, 'jni')
		if not exists(jni_ln):
			shprint(sh.ln, '-s', build_dir, jni_ln)

	def build_arch(self, arch):
		super(JpegRecipe, self).build_arch(arch)
		with current_directory(self.get_lib_dir(arch)):
			shprint(sh.mv, 'libjpeg.a', 'libjpeg-orig.a')
			shprint(sh.ar, '-rcT', 'libjpeg.a', 'libjpeg-orig.a', 'libsimd.a')


recipe = JpegRecipe()
