import unittest
from unittest import mock
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibpqRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libpq`
    """
    recipe_name = "libpq"
    sh_command_calls = ["./configure"]

    @mock.patch("pythonforandroid.recipes.libpq.sh.cp")
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
        mock_sh_cp,
    ):
        # We overwrite the base test method because we need to mock a little
        # more with this recipe (`sh.cp`)
        super(TestLibpqRecipe, self).test_build_arch()
        # make sure that the mocked methods are actually called
        mock_sh_cp.assert_called()
