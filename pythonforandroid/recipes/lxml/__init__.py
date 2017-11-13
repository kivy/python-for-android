from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import debug, shprint, info
from os.path import exists, join, dirname
import sh
import glob

class LXMLRecipe(CompiledComponentsPythonRecipe):
    version = '3.6.0'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'
    depends = ['python2', 'libxml2', 'libxslt']
    name = 'lxml'

    call_hostpython_via_targetpython = False # Due to setuptools

    def should_build(self, arch):
        super(LXMLRecipe, self).should_build(arch)
        return True
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'etree.so'))

    def build_arch(self, arch):
        super(LXMLRecipe, self).build_arch(arch)
        shutil.copyfile('%s/build/lib.linux-x86_64-2.7/lxml/etree.so' % self.get_build_dir(arch.arch), join(self.ctx.get_libs_dir(arch.arch), 'etree.so'))
        shutil.copyfile('%s/build/lib.linux-x86_64-2.7/lxml/objectify.so' % self.get_build_dir(arch.arch), join(self.ctx.get_libs_dir(arch.arch), 'objectify.so'))

    def get_recipe_env(self, arch):
        env = super(LXMLRecipe, self).get_recipe_env(arch)
        libxslt_recipe = Recipe.get_recipe('libxslt', self.ctx)
        libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)
        targetpython = "%s/include/python2.7/" % dirname(dirname(self.ctx.hostpython))
        env['CC'] += " -I%s/include -I%s -I%s" % (libxml2_recipe, libxslt_recipe, targetpython)
        env['LDSHARED'] = '%s -nostartfiles -shared -fPIC -lpython2.7' % env['CC']
        return env

recipe = LXMLRecipe()
