import unittest

from os.path import join
from unittest import mock

from pythonforandroid.recipes.hostpython3 import (
    HOSTPYTHON_VERSION_UNSET_MESSAGE, SETUP_DIST_NOT_FIND_MESSAGE,
)
from pythonforandroid.util import BuildInterruptingException
from tests.recipes.recipe_lib_test import RecipeCtx


class TestHostPython3Recipe(RecipeCtx, unittest.TestCase):
    """
    TestCase for recipe :mod:`~pythonforandroid.recipes.hostpython3`
    """
    recipe_name = "hostpython3"

    def test_property__exe_name_no_version(self):
        hostpython_version = self.recipe.version
        self.recipe._version = None
        with self.assertRaises(BuildInterruptingException) as e:
            py_exe = self.recipe._exe_name  # noqa: F841
        self.assertEqual(e.exception.args[0], HOSTPYTHON_VERSION_UNSET_MESSAGE)
        # restore recipe's version or we will get failures with other test,
        # since we share `self.recipe with all the tests of the class
        self.recipe._version = hostpython_version

    def test_property__exe_name(self):
        self.assertEqual(self.recipe._exe_name, 'python3')

    def test_property_python_exe(self):
        self.assertEqual(
            self.recipe.python_exe,
            join(self.recipe.get_path_to_python(), 'python3')
        )

    @mock.patch("pythonforandroid.recipes.hostpython3.Path.exists")
    def test_should_build(self, mock_exists):
        # test case for existing python exe which shouldn't trigger the build
        mock_exists.return_value = True
        self.assertFalse(self.recipe.should_build(self.arch))
        # test case for existing python exe which should trigger the build
        mock_exists.return_value = False
        self.assertTrue(self.recipe.should_build(self.arch))

    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.util.makedirs")
    def test_build_arch(self, mock_makedirs, mock_chdir):
        """
        Test case for
        :meth:`~pythonforandroid.recipes.python3.HostPython3Recipe.build_arch`,
        where we simulate the build for Python 3.8+.
        """

        with mock.patch(
            "pythonforandroid.recipes.hostpython3.Path.exists"
        ) as mock_path_exists, mock.patch(
            "pythonforandroid.recipes.hostpython3.sh.Command"
        ) as mock_sh_command, mock.patch(
            "pythonforandroid.recipes.hostpython3.sh.make"
        ) as mock_make, mock.patch(
            "pythonforandroid.recipes.hostpython3.Path.is_file"
        ) as mock_path_isfile, mock.patch(
            "pythonforandroid.recipes.hostpython3.sh.cp"
        ) as mock_sh_cp:
            # here we simulate the expected behaviour for Python 3.8+
            mock_path_exists.side_effect = [
                False,  # "config.status" not exists, so we trigger.configure
                False,  # "Modules/Setup.dist" shouldn't exist (3.8+ case)
                True,  # "Modules/Setup" exists, so we skip raise exception
            ]
            self.recipe.build_arch(self.arch)

        # make sure that the mocked methods are actually called
        mock_path_exists.assert_called()
        recipe_src = self.recipe.get_build_dir(self.arch.arch)
        self.assertIn(
            mock.call(f"{recipe_src}/configure"),
            mock_sh_command.mock_calls,
        )
        mock_make.assert_called()

        exe = join(self.recipe.get_path_to_python(), 'python.exe')
        mock_path_isfile.assert_called()

        self.assertEqual(mock_sh_cp.call_count, 1)
        mock_call_args, mock_call_kwargs = mock_sh_cp.call_args_list[0]
        self.assertEqual(mock_call_args[0], exe)
        self.assertEqual(mock_call_args[1], self.recipe.python_exe)
        mock_makedirs.assert_called()
        mock_chdir.assert_called()

    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.util.makedirs")
    def test_build_arch_python_lower_than_3_8(self, mock_makedirs, mock_chdir):
        """
        Test case for
        :meth:`~pythonforandroid.recipes.python3.HostPython3Recipe.build_arch`,
        where we simulate a Python 3.7 build. Here we copy an extra file:
          - Modules/Setup.dist  -> Modules/Setup.

        .. note:: We omit some checks because we already dit that at
                  `test_build_arch`. Also we skip configure command for the
                  same reason.
        """
        with mock.patch(
            "pythonforandroid.recipes.hostpython3.Path.exists"
        ) as mock_path_exists, mock.patch(
            "pythonforandroid.recipes.hostpython3.sh.make"
        ) as mock_make, mock.patch(
            "pythonforandroid.recipes.hostpython3.Path.is_file"
        ) as mock_path_isfile, mock.patch(
            "pythonforandroid.recipes.hostpython3.sh.cp"
        ) as mock_sh_cp:
            mock_path_exists.side_effect = [
                True,  # simulate that "config.status" exists to skip configure
                True,  # "Modules/Setup.dist" exist for Python 3.7
                True,  # "Modules/Setup" exists...we skip raise exception
            ]
            self.recipe.build_arch(self.arch)

        build_dir = join(
            self.recipe.get_build_dir(self.arch.arch), self.recipe.build_subdir
        )
        # we expect two calls to copy command, The one described below and the
        # copy of the python binary which already chechet at `test_build_arch`.
        self.assertEqual(mock_sh_cp.call_count, 2)
        mock_call_args, mock_call_kwargs = mock_sh_cp.call_args_list[0]
        self.assertEqual(mock_call_args[0], "Modules/Setup.dist")
        self.assertEqual(mock_call_args[1], join(build_dir, "Modules/Setup"))

        mock_path_exists.assert_called()
        mock_make.assert_called()
        mock_path_isfile.assert_called()
        mock_makedirs.assert_called()
        mock_chdir.assert_called()

    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.util.makedirs")
    def test_build_arch_setup_dist_exception(self, mock_makedirs, mock_chdir):
        """
        Test case for
        :meth:`~pythonforandroid.recipes.python3.HostPython3Recipe.build_arch`,
        where we simulate that the sources hasn't Setup.dist file, which should
        raise an exception.

        .. note:: We skip configure command because already tested at
                  `test_build_arch`.
        """
        with mock.patch(
            "pythonforandroid.recipes.hostpython3.Path.exists"
        ) as mock_path_exists:
            mock_path_exists.side_effect = [
                True,  # simulate that "config.status" exists to skip configure
                False,  # "Modules/Setup.dist" shouldn't exist (3.8+ case)
                False,  # "Modules/Setup" doesn't exists...raise exception
            ]

            with self.assertRaises(BuildInterruptingException) as e:
                self.recipe.build_arch(self.arch)
        self.assertEqual(e.exception.args[0], SETUP_DIST_NOT_FIND_MESSAGE)
        mock_makedirs.assert_called()
        mock_chdir.assert_called()
