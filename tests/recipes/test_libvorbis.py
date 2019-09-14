import unittest
from unittest import mock
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestLibvorbisRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libvorbis`
    """
    recipe_name = "libvorbis"
    sh_command_calls = ["./configure"]
    extra_env_flags = {'CFLAGS': 'libogg/include'}

    @mock.patch("pythonforandroid.recipes.libvorbis.sh.cp")
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
        super().test_build_arch()
        # make sure that the mocked methods are actually called
        mock_sh_cp.assert_called()
