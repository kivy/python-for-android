import unittest

from os.path import join
from unittest import mock

from tests.recipes.recipe_lib_test import RecipeCtx


class TestPandasRecipe(RecipeCtx, unittest.TestCase):
    """
    TestCase for recipe :mod:`~pythonforandroid.recipes.pandas`
    """
    recipe_name = "pandas"

    @mock.patch("pythonforandroid.recipe.Recipe.check_recipe_choices")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("pythonforandroid.archs.glob")
    @mock.patch("pythonforandroid.archs.find_executable")
    def test_get_recipe_env(
        self,
        mock_find_executable,
        mock_glob,
        mock_ensure_dir,
        mock_check_recipe_choices,
    ):
        """
        Test that method
        :meth:`~pythonforandroid.recipes.pandas.PandasRecipe.get_recipe_env`
        returns the expected flags
        """

        mock_find_executable.return_value = (
            "/opt/android/android-ndk/toolchains/"
            "llvm/prebuilt/linux-x86_64/bin/clang"
        )
        mock_glob.return_value = ["llvm"]
        mock_check_recipe_choices.return_value = sorted(
            self.ctx.recipe_build_order
        )
        numpy_includes = join(
            self.ctx.get_python_install_dir(), "numpy/core/include",
        )
        env = self.recipe.get_recipe_env(self.arch)
        self.assertIn(numpy_includes, env["NUMPY_INCLUDES"])
        self.assertIn(" -landroid", env["LDFLAGS"])

        # make sure that the mocked methods are actually called
        mock_glob.assert_called()
        mock_ensure_dir.assert_called()
        mock_find_executable.assert_called()
        mock_check_recipe_choices.assert_called()
