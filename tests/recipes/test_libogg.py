import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLiboggRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libogg`
    """
    recipe_name = "libogg"
    sh_command_calls = ["./configure"]
