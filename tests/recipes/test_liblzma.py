import unittest
from os.path import join
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibLzmaRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.liblzma`
    """
    recipe_name = "liblzma"
    sh_command_calls = ["./autogen.sh", "autoreconf", "./configure"]

    def test_get_library_includes(self):
        self.assertEqual(
            self.recipe.get_library_includes(self.arch),
            f" -I{join(self.recipe.get_build_dir(self.arch.arch), 'install/include')}",
        )

    def test_get_library_ldflags(self):
        self.assertEqual(
            self.recipe.get_library_ldflags(self.arch),
            f" -L{join(self.recipe.get_build_dir(self.arch.arch), 'install/lib')}",
        )

    def test_link_libs_flags(self):
        self.assertEqual(self.recipe.get_library_libs_flag(), " -llzma")
