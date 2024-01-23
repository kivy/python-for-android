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
    @mock.patch("shutil.which")
    def test_get_recipe_env(
        self,
        mock_shutil_which,
        mock_ensure_dir,
        mock_check_recipe_choices,
    ):
        """
        Test that method
        :meth:`~pythonforandroid.recipes.pandas.PandasRecipe.get_recipe_env`
        returns the expected flags
        """

        mock_shutil_which.return_value = (
            "/opt/android/android-ndk/toolchains/"
            "llvm/prebuilt/linux-x86_64/bin/clang"
        )
        mock_check_recipe_choices.return_value = sorted(
            self.ctx.recipe_build_order
        )
        numpy_includes = join(
            self.ctx.get_python_install_dir(self.arch.arch), "numpy/core/include",
        )
        env = self.recipe.get_recipe_env(self.arch)
        self.assertIn(numpy_includes, env["NUMPY_INCLUDES"])
        self.assertIn(" -landroid", env["LDFLAGS"])

        # make sure that the mocked methods are actually called
        mock_ensure_dir.assert_called()
        mock_shutil_which.assert_called()
        mock_check_recipe_choices.assert_called()
