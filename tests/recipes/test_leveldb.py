import unittest
from tests.recipes.recipe_lib_test import BaseTestForCmakeRecipe


class TestLeveldbRecipe(BaseTestForCmakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.leveldb`
    """
    recipe_name = "leveldb"
