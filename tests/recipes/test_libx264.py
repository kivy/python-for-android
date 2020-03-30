import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibx264Recipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libx264`
    """
    recipe_name = "libx264"
    sh_command_calls = ["./configure"]
