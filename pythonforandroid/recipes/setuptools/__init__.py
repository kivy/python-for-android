from os.path import exists, join
from pythonforandroid.logger import info
from pythonforandroid.recipe import PythonRecipe


class SetuptoolsRecipe(PythonRecipe):
    version = '69.0.3'
    hostpython_prerequisites = ["setuptools=={}".format(version)]

    def should_build(self, arch):
        if exists(join(self.hostpython_site_dir, "setuptools")):
            info('Python package already exists in site-packages')
            return False
        info('setuptools apparently isn\'t already in site-packages')
        return True

    def build_arch(self, arch):
        self.install_hostpython_prerequisites()


recipe = SetuptoolsRecipe()
