import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibiconvRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libiconv`
    """
    recipe_name = "libiconv"
    sh_command_calls = ["./configure"]
