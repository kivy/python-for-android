import unittest
from tests.recipes.recipe_lib_test import BaseTestForCmakeRecipe


class TestJpegRecipe(BaseTestForCmakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.jpeg`
    """
    recipe_name = "jpeg"
