import os
import unittest
from unittest import mock

from tests.recipes.recipe_ctx import RecipeCtx
from pythonforandroid.recipes.icu import ICURecipe


class TestIcuRecipe(RecipeCtx, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.icu`
    """

    recipe_name = "icu"

    def test_url(self):
        self.assertTrue(self.recipe.versioned_url.startswith("http"))
        self.assertIn(self.recipe.version.replace('.', '-'), self.recipe.versioned_url)

    @mock.patch(
        "pythonforandroid.recipe.Recipe.url", new_callable=mock.PropertyMock
    )
    def test_url_none(self, mock_url):
        mock_url.return_value = None
        self.assertIsNone(self.recipe.versioned_url)

    def test_get_recipe_dir(self):
        expected_dir = os.path.join(self.ctx.root_dir, "recipes", "icu")
        self.assertEqual(self.recipe.get_recipe_dir(), expected_dir)

    @mock.patch("pythonforandroid.util.makedirs")
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.bootstrap.sh.Command")
    @mock.patch("pythonforandroid.recipes.icu.sh.make")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("shutil.which")
    def test_build_arch(
        self,
        mock_shutil_which,
        mock_ensure_dir,
        mock_sh_make,
        mock_sh_command,
        mock_chdir,
        mock_makedirs,
    ):
        mock_shutil_which.return_value = os.path.join(
            self.ctx._ndk_dir,
            f"toolchains/llvm/prebuilt/{self.ctx.ndk.host_tag}/bin/clang",
        )
        self.ctx.toolchain_version = "4.9"
        self.recipe.build_arch(self.arch)

        # We expect some calls to `sh.Command`
        build_root = self.recipe.get_build_dir(self.arch.arch)
        mock_sh_command.has_calls(
            [
                mock.call(
                    os.path.join(build_root, "source", "runConfigureICU")
                ),
                mock.call(os.path.join(build_root, "source", "configure")),
            ]
        )
        mock_ensure_dir.assert_called()
        mock_chdir.assert_called()
        # we expect multiple calls to sh.make command
        expected_host_cppflags = (
            "-O3 -fno-short-wchar -DU_USING_ICU_NAMESPACE=1 -fno-short-enums "
            "-DU_HAVE_NL_LANGINFO_CODESET=0 -D__STDC_INT64__ -DU_TIMEZONE=0 "
            "-DUCONFIG_NO_LEGACY_CONVERSION=1 "
            "-DUCONFIG_NO_TRANSLITERATION=0 "
        )
        for call_number, call in enumerate(mock_sh_make.call_args_list):
            # here we expect to find the compile command  `make -j`in first and
            # third calls, the others should be the  `make install` commands
            is_host_build = call_number in [0, 1]
            is_compile = call_number in [0, 2]
            call_args, call_kwargs = call
            self.assertTrue(
                call_args[0].startswith("-j" if is_compile else "install")
            )
            self.assertIn("_env", call_kwargs)
            if is_host_build:
                self.assertIn(
                    expected_host_cppflags, call_kwargs["_env"]["CPPFLAGS"]
                )
            else:
                self.assertNotIn(
                    expected_host_cppflags, call_kwargs["_env"]["CPPFLAGS"]
                )
        mock_makedirs.assert_called()

        mock_shutil_which.assert_called_once()
        self.assertEqual(
            mock_shutil_which.call_args[0][0],
            mock_shutil_which.return_value,
        )

    @mock.patch("pythonforandroid.recipes.icu.sh.cp")
    @mock.patch("pythonforandroid.util.makedirs")
    def test_install_libraries(self, mock_makedirs, mock_sh_cp):
        self.recipe.install_libraries(self.arch)
        mock_makedirs.assert_called()
        mock_sh_cp.assert_called()

    @mock.patch("pythonforandroid.recipes.icu.exists")
    def test_get_recipe_dir_with_local_recipes(self, mock_exists):
        self.ctx.local_recipes = "/home/user/p4a_local_recipes"

        # we don't use `self.recipe` because, somehow, the modified variable
        # above is not updated in the `ctx` and makes the test fail...
        recipe = ICURecipe()
        recipe.ctx = self.ctx
        recipe_dir = recipe.get_recipe_dir()

        expected_dir = os.path.join(self.ctx.local_recipes, "icu")
        self.assertEqual(recipe_dir, expected_dir)
        mock_exists.assert_called_once_with(expected_dir)
