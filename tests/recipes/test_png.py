import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestPngRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.png`
    """
    recipe_name = "png"
    sh_command_calls = ["./configure"]
