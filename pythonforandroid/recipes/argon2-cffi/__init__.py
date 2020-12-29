from pythonforandroid.toolchain import Recipe, shprint, current_directory
from os.path import exists, join
import sh
import glob


class YourRecipe(Recipe):
    # This could also inherit from PythonRecipe etc. if you want to
    # use their pre-written build processes

    version = '20.1.0'
    url = 'https://github.com/hynek/argon2-cffi/archive/master.zip'
    # {version} will be replaced with self.version when downloading

    depends = ['setuptools', 'cffi']  # A list of any other recipe names
                                    # that must be built before this
                                    # one

    conflicts = []  # A list of any recipe names that cannot be built
                    # alongside this one

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # Manipulate the env here if you want
        return env

    def should_build(self, arch):
        # Add a check for whether the recipe is already built if you
        # want, and return False if it is.
        return True

    def prebuild_arch(self, arch):
        super().prebuild_arch(self)
        # Do any extra prebuilding you want, e.g.:
        self.apply_patch('path/to/patch.patch')

    def build_arch(self, arch):
        print('AAAAAAAA@@I was called@@AAAAAAAA')
        super().build_arch(self)
        # Build the code. Make sure to use the right build dir, e.g.
        with current_directory(self.get_build_dir(arch.arch)):
            sh.ls('-lathr')  # Or run some commands that actually do
                             # something

    def postbuild_arch(self, arch):
        super().prebuild_arch(self)
        # Do anything you want after the build, e.g. deleting
        # unnecessary files such as documentation


recipe = YourRecipe()