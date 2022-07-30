from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe
from pythonforandroid.util import ensure_dir

from os.path import join


class MatplotlibRecipe(CppCompiledComponentsPythonRecipe):

    version = '3.5.2'
    url = 'https://github.com/matplotlib/matplotlib/archive/v{version}.zip'

    depends = ['kiwisolver', 'numpy', 'pillow', 'setuptools', 'freetype']

    python_depends = ['cycler', 'fonttools', 'packaging', 'pyparsing', 'python-dateutil']

    # We need to patch to:
    # - make mpl install work without importing numpy
    # - make mpl use shared libraries for freetype and png
    # - make mpl link to png16, to match p4a library name for png
    # - prevent mpl trying to build TkAgg, which wouldn't work
    #   on Android anyway but has build issues
    # patches = ['mpl_android_fixes.patch']

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
        with open(join(self.get_recipe_dir(), 'setup.cfg.template')) as fileh:
            setup_cfg = fileh.read()

        with open(join(self.get_build_dir(arch), 'mplsetup.cfg'), 'w') as fileh:
            fileh.write(setup_cfg.format(
                ndk_sysroot_usr=join(self.ctx.ndk.sysroot, 'usr')))

        self.generate_libraries_pc_files(arch)

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)

        # we modify `XDG_CACHE_HOME` to download `jquery-ui` into that folder,
        # or mpl install will fail when trying to download/install it, but if
        # we have the proper package already downloaded, it will use the cached
        # package to successfully finish the installation.
        # Note: this may not be necessary for some local systems, but it is
        #       for our CI provider: `gh-actions`, which will
        #       fail trying to download the `jquery-ui` package
        env['XDG_CACHE_HOME'] = join(self.get_build_dir(arch), 'p4a_files')
        # we make use of the same directory than `XDG_CACHE_HOME`, for our
        # custom library pc files, so we have all the install files that we
        # generate at the same place
        env['PKG_CONFIG_PATH'] = env['XDG_CACHE_HOME']

        # We set a new environ variable `NUMPY_INCLUDES` to be able to tell
        # the matplotlib script where to find our numpy without importing it
        # (which will fail, because numpy isn't installed in our hostpython)
        env['NUMPY_INCLUDES'] = join(
            self.ctx.get_site_packages_dir(arch),
            'numpy', 'core', 'include',
        )

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
