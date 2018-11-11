import os
import tempfile
import unittest
from mock import patch
from pythonforandroid.archs import ArchARMv7_a
from pythonforandroid.build import Context
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import ensure_dir


class TestReportLabRecipe(unittest.TestCase):

    def setUp(self):
        """
        Setups recipe and context.
        """
        self.context = Context()
        self.context.ndk_api = 21
        self.context.android_api = 27
        self.arch = ArchARMv7_a(self.context)
        self.recipe = Recipe.get_recipe('reportlab', self.context)
        self.recipe.ctx = self.context
        self.bootstrap = None
        recipe_build_order, python_modules, bootstrap = \
            get_recipe_order_and_bootstrap(
                self.context, [self.recipe.name], self.bootstrap)
        self.context.recipe_build_order = recipe_build_order
        self.context.python_modules = python_modules
        self.context.setup_dirs(tempfile.gettempdir())
        self.bootstrap = bootstrap
        self.recipe_dir = self.recipe.get_build_dir(self.arch.arch)
        ensure_dir(self.recipe_dir)

    def test_prebuild_arch(self):
        """
        Makes sure `prebuild_arch()` runs without error and patches `setup.py`
        as expected.
        """
        # `prebuild_arch()` dynamically replaces strings in the `setup.py` file
        setup_path = os.path.join(self.recipe_dir, 'setup.py')
        with open(setup_path, 'w') as setup_file:
            setup_file.write('_FT_LIB_\n')
            setup_file.write('_FT_INC_\n')

        # these sh commands are not relevant for the test and need to be mocked
        with \
                patch('sh.patch'), \
                patch('sh.touch'), \
                patch('sh.unzip'), \
                patch('os.path.isfile'):
            self.recipe.prebuild_arch(self.arch)
        # makes sure placeholder got replaced with library and include paths
        with open(setup_path, 'r') as setup_file:
            lines = setup_file.readlines()
        self.assertTrue(lines[0].endswith('freetype/objs/.libs\n'))
        self.assertTrue(lines[1].endswith('freetype/include\n'))
