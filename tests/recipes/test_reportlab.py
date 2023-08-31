import os
import unittest
from unittest.mock import patch
from tests.recipes.recipe_ctx import RecipeCtx
from pythonforandroid.util import ensure_dir


class TestReportLabRecipe(RecipeCtx, unittest.TestCase):
    recipe_name = "reportlab"

    def setUp(self):
        """
        Setups recipe and context.
        """
        super().setUp()
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
                patch('pythonforandroid.recipe.touch'), \
                patch('sh.unzip'), \
                patch('os.path.isfile'):
            self.recipe.prebuild_arch(self.arch)
        # makes sure placeholder got replaced with library and include paths
        with open(setup_path, 'r') as setup_file:
            lines = setup_file.readlines()
        self.assertTrue(lines[0].endswith('freetype/objs/.libs\n'))
        self.assertTrue(lines[1].endswith('freetype/include\n'))
