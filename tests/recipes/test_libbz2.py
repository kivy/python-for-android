import unittest

from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibBz2Recipe(BaseTestForMakeRecipe, unittest.TestCase):
    """TestCase for recipe :mod:`~pythonforandroid.recipes.libbz2`."""
    recipe_name = "libbz2"
    sh_command_calls = []

    def test_get_library_includes(self):
        """
        Test :meth:`~pythonforandroid.recipes.libbz2.get_library_includes`.
        """
        self.assertEqual(
            self.recipe.get_library_includes(self.arch),
            f" -I{self.recipe.get_build_dir(self.arch.arch)}",
        )

    def test_get_library_ldflags(self):
        """
        Test :meth:`~pythonforandroid.recipes.libbz2.get_library_ldflags`.
        """
        self.assertEqual(
            self.recipe.get_library_ldflags(self.arch),
            f" -L{self.recipe.get_build_dir(self.arch.arch)}",
        )

    def test_link_libs_flags(self):
        """
        Test :meth:`~pythonforandroid.recipes.libbz2.get_library_ldflags`.
        """
        self.assertEqual(self.recipe.get_library_libs_flag(), " -lbz2")
