import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibshineRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libshine`
    """
    recipe_name = "libshine"
    sh_command_calls = ["./bootstrap", "./configure"]
