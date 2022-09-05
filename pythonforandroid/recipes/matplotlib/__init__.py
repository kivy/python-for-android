from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe
from pythonforandroid.util import ensure_dir

from os.path import join
import shutil


class MatplotlibRecipe(CppCompiledComponentsPythonRecipe):

    version = '3.5.2'
    url = 'https://github.com/matplotlib/matplotlib/archive/v{version}.zip'

    depends = ['kiwisolver', 'numpy', 'pillow', 'setuptools', 'freetype']

    python_depends = ['cycler', 'fonttools', 'packaging', 'pyparsing', 'python-dateutil']

    def generate_libraries_pc_files(self, arch):
        """
        Create *.pc files for libraries that `matplotib` depends on.

        Because, for unix platforms, the mpl install script uses `pkg-config`
        to detect libraries installed in non standard locations (our case...
        well...we don't even install the libraries...so we must trick a little
        the mlp install).
        """
        pkg_config_path = self.get_recipe_env(arch)['PKG_CONFIG_PATH']
        ensure_dir(pkg_config_path)

        lib_to_pc_file = {
            # `pkg-config` search for version freetype2.pc, our current
            # version for freetype, but we have our recipe named without
            # the version...so we add it in here for our pc file
            'freetype': 'freetype2.pc',
        }

        for lib_name in {'freetype'}:
            pc_template_file = join(
                self.get_recipe_dir(),
                f'lib{lib_name}.pc.template'
            )
            # read template file into buffer
            with open(pc_template_file) as template_file:
                text_buffer = template_file.read()
            # set the library absolute path and library version
            lib_recipe = self.get_recipe(lib_name, self.ctx)
            text_buffer = text_buffer.replace(
                'path_to_built', lib_recipe.get_build_dir(arch.arch),
            )
            text_buffer = text_buffer.replace(
                'library_version', lib_recipe.version,
            )

            # write the library pc file into our defined dir `PKG_CONFIG_PATH`
            pc_dest_file = join(pkg_config_path, lib_to_pc_file[lib_name])
            with open(pc_dest_file, 'w') as pc_file:
                pc_file.write(text_buffer)

    def prebuild_arch(self, arch):
        shutil.copyfile(
            join(self.get_recipe_dir(), "setup.cfg.template"),
            join(self.get_build_dir(arch), "mplsetup.cfg"),
        )
        self.generate_libraries_pc_files(arch)

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)

        # we make use of the same directory than `XDG_CACHE_HOME`, for our
        # custom library pc files, so we have all the install files that we
        # generate at the same place
        env['XDG_CACHE_HOME'] = join(self.get_build_dir(arch), 'p4a_files')
        env['PKG_CONFIG_PATH'] = env['XDG_CACHE_HOME']

        # creating proper *.pc files for our libraries does not seem enough to
        # success with our build (without depending on system development
        # libraries), but if we tell the compiler where to find our libraries
        # and includes, then the install success :)
        freetype = self.get_recipe('freetype', self.ctx)
        free_lib_dir = join(freetype.get_build_dir(arch.arch), 'objs', '.libs')
        free_inc_dir = join(freetype.get_build_dir(arch.arch), 'include')
        env['CFLAGS'] += f' -I{free_inc_dir}'
        env['LDFLAGS'] += f' -L{free_lib_dir}'

        # `freetype` could be built with `harfbuzz` support,
        # so we also include the necessary flags...just to be sure
        if 'harfbuzz' in self.ctx.recipe_build_order:
            harfbuzz = self.get_recipe('harfbuzz', self.ctx)
            harf_build = harfbuzz.get_build_dir(arch.arch)
            env['CFLAGS'] += f' -I{harf_build} -I{join(harf_build, "src")}'
            env['LDFLAGS'] += f' -L{join(harf_build, "src", ".libs")}'
        return env


recipe = MatplotlibRecipe()
