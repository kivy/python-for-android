import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibexpatRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libexpat`
    """
    recipe_name = "libexpat"
    sh_command_calls = ["./buildconf.sh", "./configure"]
