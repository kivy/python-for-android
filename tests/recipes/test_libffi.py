import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibffiRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libffi`
    """
    recipe_name = "libffi"
    sh_command_calls = ["./autogen.sh", "autoreconf", "./configure"]

    def test_get_include_dirs(self):
        list_of_includes = self.recipe.get_include_dirs(self.arch)
        self.assertIsInstance(list_of_includes, list)
        self.assertTrue(list_of_includes[0].endswith("include"))
