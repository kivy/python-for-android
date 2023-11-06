import unittest
from unittest import mock
from tests.recipes.recipe_lib_test import BaseTestForCmakeRecipe


class TestLibmysqlclientRecipe(BaseTestForCmakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.libmysqlclient`
    """
    recipe_name = "libmysqlclient"

    @mock.patch("pythonforandroid.recipes.libmysqlclient.sh.rm")
    @mock.patch("pythonforandroid.recipes.libmysqlclient.sh.cp")
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("shutil.which")
    def test_build_arch(
        self,
        mock_shutil_which,
        mock_ensure_dir,
        mock_current_directory,
        mock_sh_cp,
        mock_sh_rm,
    ):
        # We overwrite the base test method because we need
        # to mock a little more (`sh.cp` and rmdir)
        super().test_build_arch()
        # make sure that the mocked methods are actually called
        mock_sh_cp.assert_called()
        mock_sh_rm.assert_called()
