import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibcurlRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libcurl`
    """
    recipe_name = "libcurl"
    sh_command_calls = ["./configure"]
