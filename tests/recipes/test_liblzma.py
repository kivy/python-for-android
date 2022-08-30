import unittest
from os.path import join
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibLzmaRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """TestCase for recipe :mod:`~pythonforandroid.recipes.liblzma`."""
    recipe_name = "liblzma"
    sh_command_calls = ["./autogen.sh", "autoreconf", "./configure"]

    def test_get_library_includes(self):
        """
        Test :meth:`~pythonforandroid.recipes.liblzma.get_library_includes`.
        """
        recipe_build_dir = self.recipe.get_build_dir(self.arch.arch)
        self.assertEqual(
            self.recipe.get_library_includes(self.arch),
            f" -I{join(recipe_build_dir, 'p4a_install/include')}",
        )

    def test_get_library_ldflags(self):
        """
        Test :meth:`~pythonforandroid.recipes.liblzma.get_library_ldflags`.
        """
        recipe_build_dir = self.recipe.get_build_dir(self.arch.arch)
        self.assertEqual(
            self.recipe.get_library_ldflags(self.arch),
            f" -L{join(recipe_build_dir, 'p4a_install/lib')}",
        )

    def test_link_libs_flags(self):
        """
        Test :meth:`~pythonforandroid.recipes.liblzma.get_library_libs_flag`.
        """
        self.assertEqual(self.recipe.get_library_libs_flag(), " -llzma")

    def test_install_dir_not_named_install(self):
        """
        Tests that the install directory is not named ``install``.

        liblzma already have a file named ``INSTALL`` in its source directory.
        On case-insensitive filesystems, using a folder named ``install`` will
        cause a conflict. (See issue: #2343).

        WARNING: This test is quite flaky, but should be enough to
        ensure that someone in the future will not accidentally rename
        the install directory without seeing this test to fail.
        """
        liblzma_install_dir = self.recipe.built_libraries["liblzma.so"]

        self.assertNotIn("install", liblzma_install_dir.split("/"))
