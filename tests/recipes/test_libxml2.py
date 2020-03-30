import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibxml2Recipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libxml2`
    """
    recipe_name = "libxml2"
    sh_command_calls = ["./autogen.sh", "autoreconf", "./configure"]
    extra_env_flags = {
        "CONFIG_SHELL": "/bin/bash",
        "SHELL": "/bin/bash",
    }
