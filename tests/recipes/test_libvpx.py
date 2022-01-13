import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibVPXRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libvpx`
    """
    recipe_name = "libvpx"
    sh_command_calls = ["./configure"]
