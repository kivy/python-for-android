import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestFreetypeRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.freetype`
    """
    recipe_name = "freetype"
    sh_command_calls = ["./configure"]
