import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestHarfbuzzRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.harfbuzz`
    """
    recipe_name = "harfbuzz"
    sh_command_calls = ["./configure"]
