import unittest
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibxsltRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libxslt`
    """
    recipe_name = "libxslt"
    sh_command_calls = ["./autogen.sh", "autoreconf", "./configure"]
    extra_env_flags = {
        "CONFIG_SHELL": "/bin/bash",
        "SHELL": "/bin/bash",
        "LIBS": "-lxml2 -lz -lm",
    }
