from pythonforandroid.recipe import Recipe, CompiledComponentsPythonRecipe
from os.path import exists, join
from os import uname


class LXMLRecipe(CompiledComponentsPythonRecipe):
    version = '4.2.5'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'  # noqa
    depends = ['librt', 'libxml2', 'libxslt', 'setuptools']
    name = 'lxml'

    call_hostpython_via_targetpython = False  # Due to setuptools

    def should_build(self, arch):
        super().should_build(arch)

        py_ver = self.ctx.python_recipe.major_minor_version_string
        build_platform = '{system}-{machine}'.format(
            system=uname()[0], machine=uname()[-1]).lower()
        build_dir = join(self.get_build_dir(arch.arch), 'build',
                         'lib.' + build_platform + '-' + py_ver, 'lxml')
        py_libs = ['_elementpath.so', 'builder.so', 'etree.so', 'objectify.so']

        return not all([exists(join(build_dir, lib)) for lib in py_libs])

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        # libxslt flags
        libxslt_recipe = Recipe.get_recipe('libxslt', self.ctx)
        libxslt_build_dir = libxslt_recipe.get_build_dir(arch.arch)

        cflags = ' -I' + libxslt_build_dir
        cflags += ' -I' + join(libxslt_build_dir, 'libxslt')
        cflags += ' -I' + join(libxslt_build_dir, 'libexslt')

        env['LDFLAGS'] += ' -L' + join(libxslt_build_dir, 'libxslt', '.libs')
        env['LDFLAGS'] += ' -L' + join(libxslt_build_dir, 'libexslt', '.libs')
        env['LIBS'] = '-lxslt -lexslt'

        # libxml2 flags
        libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)
        libxml2_build_dir = libxml2_recipe.get_build_dir(arch.arch)
        libxml2_libs_dir = join(libxml2_build_dir, '.libs')

        cflags += ' -I' + libxml2_build_dir
        cflags += ' -I' + join(libxml2_build_dir, 'include')
        cflags += ' -I' + join(libxml2_build_dir, 'include', 'libxml')
        cflags += ' -I' + self.get_build_dir(arch.arch)
        env['LDFLAGS'] += ' -L' + libxml2_libs_dir
        env['LIBS'] += ' -lxml2'

        # android's ndk flags
        ndk_lib_dir = join(self.ctx.ndk_platform, 'usr', 'lib')
        ndk_include_dir = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')
        cflags += ' -I' + ndk_include_dir
        env['LDFLAGS'] += ' -L' + ndk_lib_dir
        env['LIBS'] += ' -lz -lm -lc'

        if cflags not in env['CFLAGS']:
            env['CFLAGS'] += cflags

        return env


recipe = LXMLRecipe()
