import unittest
from tests.recipes.recipe_lib_test import BaseTestForCmakeRecipe


class TestSnappyRecipe(BaseTestForCmakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.snappy`
    """
    recipe_name = "snappy"
