import unittest
from unittest import mock
from tests.recipes.recipe_lib_test import BaseTestForCmakeRecipe


class TestLibgeosRecipe(BaseTestForCmakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libgeos`
    """
    recipe_name = "libgeos"

    @mock.patch("pythonforandroid.util.makedirs")
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("pythonforandroid.archs.glob")
    @mock.patch("pythonforandroid.archs.find_executable")
    def test_build_arch(
        self,
        mock_find_executable,
        mock_glob,
        mock_ensure_dir,
        mock_current_directory,
        mock_makedirs,
    ):
        # We overwrite the base test method because we
        # want to avoid any file/directory creation
        super().test_build_arch()
        # make sure that the mocked methods are actually called
        mock_makedirs.assert_called()
