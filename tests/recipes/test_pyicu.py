import os

import unittest

try:
    from unittest import mock
except ImportError:
    # `Python 2` or lower than `Python 3.3` does not
    # have the `unittest.mock` module built-in
    import mock
from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.distribution import Distribution
from pythonforandroid.recipe import Recipe
from pythonforandroid.build import Context
from pythonforandroid.archs import ArchARMv7_a


class TestPyIcuRecipe(unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.pyicu`
    """

    ctx = None

    def setUp(self):
        self.ctx = Context()
        self.ctx.ndk_api = 21
        self.ctx.android_api = 27
        self.ctx._sdk_dir = "/opt/android/android-sdk"
        self.ctx._ndk_dir = "/opt/android/android-ndk"
        self.ctx.setup_dirs(os.getcwd())
        self.ctx.bootstrap = Bootstrap().get_bootstrap("sdl2", self.ctx)
        self.ctx.bootstrap.distribution = Distribution.get_distribution(
            self.ctx, name="sdl2", recipes=["python3", "kivy", "pyicu"]
        )
        self.ctx.recipe_build_order = [
            "hostpython3",
            "icu",
            "python3",
            "sdl2",
            "pyicu",
            "kivy",
        ]
        self.ctx.python_recipe = Recipe.get_recipe("python3", self.ctx)

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
        :meth:`~pythonforandroid.recipes.pyicu.PyICURecipe.get_recipe_env`
        returns the expected flags
        """
        arch = ArchARMv7_a(self.ctx)
        recipe = Recipe.get_recipe("pyicu", self.ctx)

        icu_recipe = Recipe.get_recipe("icu", self.ctx)

        mock_find_executable.return_value = (
            "/opt/android/android-ndk/toolchains/"
            "llvm/prebuilt/linux-x86_64/bin/clang"
        )
        mock_glob.return_value = ["llvm"]
        mock_check_recipe_choices.return_value = sorted(
            self.ctx.recipe_build_order
        )

        expected_pyicu_libs = [
            lib[3:-3] for lib in icu_recipe.built_libraries.keys()
        ]
        env = recipe.get_recipe_env(arch)
        self.assertEqual(":".join(expected_pyicu_libs), env["PYICU_LIBRARIES"])
        self.assertIn("include/icu", env["CPPFLAGS"])
        self.assertIn("icu4c/icu_build/lib", env["LDFLAGS"])

        # make sure that the mocked methods are actually called
        mock_glob.assert_called()
        mock_ensure_dir.assert_called()
        mock_find_executable.assert_called()
        mock_check_recipe_choices.assert_called()
