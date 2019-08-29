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

from pythonforandroid.build import Context
from pythonforandroid.archs import ArchARMv7_a
from pythonforandroid.recipes.icu import ICURecipe
from pythonforandroid.recipe import Recipe


class TestIcuRecipe(unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.icu`
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
            self.ctx, name="sdl2", recipes=["python3", "kivy", "icu"]
        )
        self.ctx.python_recipe = ICURecipe.get_recipe("python3", self.ctx)
        self.ctx.recipe_build_order = [
            "hostpython3",
            "icu",
            "python3",
            "sdl2",
            "kivy",
        ]

    def tearDown(self):
        self.ctx = None

    def test_url(self):
        recipe = ICURecipe()
        recipe.ctx = self.ctx
        self.assertTrue(recipe.versioned_url.startswith("http"))
        self.assertIn(recipe.version, recipe.versioned_url)

    @mock.patch(
        "pythonforandroid.recipe.Recipe.url", new_callable=mock.PropertyMock
    )
    def test_url_none(self, mock_url):
        mock_url.return_value = None
        recipe = ICURecipe()
        recipe.ctx = self.ctx
        self.assertIsNone(recipe.versioned_url)

    def test_get_recipe_dir(self):
        recipe = ICURecipe()
        recipe.ctx = self.ctx
        expected_dir = os.path.join(self.ctx.root_dir, "recipes", "icu")
        self.assertEqual(recipe.get_recipe_dir(), expected_dir)

    @mock.patch("pythonforandroid.util.makedirs")
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.bootstrap.sh.Command")
    @mock.patch("pythonforandroid.recipes.icu.sh.make")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("pythonforandroid.archs.glob")
    @mock.patch("pythonforandroid.archs.find_executable")
    def test_build_arch(
        self,
        mock_find_executable,
        mock_archs_glob,
        mock_ensure_dir,
        mock_sh_make,
        mock_sh_command,
        mock_chdir,
        mock_makedirs,
    ):
        recipe = ICURecipe()
        recipe.ctx = self.ctx
        mock_find_executable.return_value = os.path.join(
            self.ctx._ndk_dir,
            "toolchains/llvm/prebuilt/linux-x86_64/bin/clang",
        )
        mock_archs_glob.return_value = [
            os.path.join(self.ctx._ndk_dir, "toolchains", "llvm")
        ]
        arch = ArchARMv7_a(self.ctx)
        self.ctx.toolchain_prefix = arch.toolchain_prefix
        self.ctx.toolchain_version = "4.9"
        recipe.build_arch(arch)

        # We expect to calls to `sh.Command`
        build_root = recipe.get_build_dir(arch.arch)
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
        # we expect for calls to sh.make command
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

        mock_find_executable.assert_called_once()
        self.assertEqual(
            mock_find_executable.call_args[0][0],
            mock_find_executable.return_value,
        )

    @mock.patch("pythonforandroid.recipes.icu.sh.cp")
    @mock.patch("pythonforandroid.util.makedirs")
    def test_install_libraries(self, mock_makedirs, mock_sh_cp):
        arch = ArchARMv7_a(self.ctx)
        recipe = Recipe.get_recipe("icu", self.ctx)
        recipe.ctx = self.ctx
        recipe.install_libraries(arch)
        mock_makedirs.assert_called()
        mock_sh_cp.assert_called()

    @mock.patch("pythonforandroid.recipes.icu.exists")
    def test_get_recipe_dir_with_local_recipes(self, mock_exists):
        self.ctx.local_recipes = "/home/user/p4a_local_recipes"

        recipe = ICURecipe()
        recipe.ctx = self.ctx
        recipe_dir = recipe.get_recipe_dir()

        expected_dir = os.path.join(self.ctx.local_recipes, "icu")
        self.assertEqual(recipe_dir, expected_dir)
        mock_exists.assert_called_once_with(expected_dir)
