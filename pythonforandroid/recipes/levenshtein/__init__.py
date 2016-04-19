from pythonforandroid.toolchain import CompiledComponentsPythonRecipe
from os.path import dirname

class LevenshteinRecipe(CompiledComponentsPythonRecipe):
    name="levenshtein"
    version = '0.12.0'
    url = 'https://pypi.python.org/packages/source/p/python-Levenshtein/python-Levenshtein-{version}.tar.gz'
    depends = [('python2', 'python3'), 'setuptools']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(LevenshteinRecipe, self).get_recipe_env(arch)
        libxslt_recipe = Recipe.get_recipe('libxslt', self.ctx)
        libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)
        targetpython = "%s/include/python2.7/" % dirname(dirname(self.ctx.hostpython))
        env['CC'] += " -I%s/include -I%s -I%s" % (libxml2_recipe, libxslt_recipe, targetpython)
        env['LDSHARED'] = '%s -nostartfiles -shared -fPIC -lpython2.7' % env['CC']
        return env

recipe = LevenshteinRecipe()
