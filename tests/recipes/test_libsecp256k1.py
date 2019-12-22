import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibsecp256k1Recipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libsecp256k1`
    """
    recipe_name = "libsecp256k1"
    sh_command_calls = ["./autogen.sh", "./configure"]
