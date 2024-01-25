from os.path import exists, join
from pythonforandroid.logger import info
from pythonforandroid.recipe import PythonRecipe


# A very hacky recipe
# This avoids hassle of finding and correctly linking libffi
# and just works


class CffiRecipe(PythonRecipe):
    version = "1.15.1"
    hostpython_prerequisites = ["cffi=={}".format(version), "pycparser"]

    def should_build(self, arch):
        if exists(join(self.hostpython_site_dir, "cffi")):
            info('Python package already exists in site-packages')
            return False
        info('cffi apparently isn\'t already in site-packages')
        return True

    def build_arch(self, arch):
        self.install_hostpython_prerequisites()


recipe = CffiRecipe()
