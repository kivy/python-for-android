from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from multiprocessing import cpu_count
import os
import sh


class TesseractRecipe(Recipe):
    version = '3.05.02'
    url = 'https://github.com/tesseract-ocr/tesseract/archive/{version}.tar.gz'
    md5sum = 'd3b8661f878aed931cf3a7595e69b989'
    sha256sum = '494d64ffa7069498a97b909a0e65a35a213989e0184f1ea15332933a90d43445'

    depends = ['libleptonica']
    need_stl_shared = True
    built_libraries = {'libtesseract.so': os.path.join('api', '.libs')}
    patches = ['android_rt.patch', 'remove-version-info-3.patch']

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        env['PKG_CONFIG_PATH'] = env.get('PKG_CONFIG_PATH', '') + ':' + os.path.join(
            self.get_recipe('libleptonica', self.ctx).get_build_dir(arch.arch),
            'install', 'lib', 'pkgconfig'
        )
        env['CPPFLAGS'] = env.get('CPPFLAGS', '') + ' -I{}'.format(self.stl_include_dir)
        env['LDFLAGS'] = env.get('LDFLAGS', '') + ' -L{} -l{}'.format(self.get_stl_lib_dir(arch), self.stl_lib_name)
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        source_dir = self.get_build_dir(arch.arch)
        install_dir = self.ctx.get_python_install_dir()

        with current_directory(source_dir):
            shprint(sh.Command('./autogen.sh'))
            shprint(
                sh.Command('./configure'),
                '--host={}'.format(arch.command_prefix),
                '--target={}'.format(arch.toolchain_prefix),
                '--prefix={}'.format(install_dir),
                '--enable-embedded',
                '--enable-shared=yes',
                '--enable-static=no',
                'ac_cv_c_bigendian=no',
                'ac_cv_sys_file_offset_bits=32',
                _env=env)
            shprint(sh.make, '-j' + str(cpu_count() + 1), _env=env)

            # make the install so the headers are collected in the right subfolder
            shprint(sh.make, 'install', _env=env)


recipe = TesseractRecipe()
