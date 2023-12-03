import unittest
from unittest import mock
from tests.recipes.recipe_ctx import RecipeCtx
from pythonforandroid.recipe import Recipe


class TestPyIcuRecipe(RecipeCtx, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.pyicu`
    """
    recipe_name = "pyicu"

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
        :meth:`~pythonforandroid.recipes.pyicu.PyICURecipe.get_recipe_env`
        returns the expected flags
        """
        icu_recipe = Recipe.get_recipe("icu", self.ctx)

        mock_shutil_which.return_value = (
            "/opt/android/android-ndk/toolchains/"
            "llvm/prebuilt/linux-x86_64/bin/clang"
        )
        mock_check_recipe_choices.return_value = sorted(
            self.ctx.recipe_build_order
        )

        expected_pyicu_libs = [
            lib[3:-3] for lib in icu_recipe.built_libraries.keys()
        ]
        env = self.recipe.get_recipe_env(self.arch)
        self.assertEqual(":".join(expected_pyicu_libs), env["PYICU_LIBRARIES"])
        self.assertIn("include/icu", env["CPPFLAGS"])
        self.assertIn("icu4c/icu_build/lib", env["LDFLAGS"])

        # make sure that the mocked methods are actually called
        mock_ensure_dir.assert_called()
        mock_shutil_which.assert_called()
        mock_check_recipe_choices.assert_called()
