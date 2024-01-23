import unittest
from unittest import mock
from tests.recipes.recipe_lib_test import BaseTestForMakeRecipe


class TestOpensslRecipe(BaseTestForMakeRecipe, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.openssl`
    """

    recipe_name = "openssl"
    sh_command_calls = ["perl"]

    @mock.patch("pythonforandroid.recipes.openssl.sh.patch")
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("shutil.which")
    def test_build_arch(
        self,
        mock_shutil_which,
        mock_ensure_dir,
        mock_current_directory,
        mock_sh_patch,
    ):
        # We overwrite the base test method because we need to mock a little
        # more with this recipe.
        super().test_build_arch()
        # make sure that the mocked methods are actually called
        mock_sh_patch.assert_called()

    def test_versioned_url(self):
        self.assertEqual(
            self.recipe.url.format(url_version=self.recipe.url_version),
            self.recipe.versioned_url,
        )

    def test_include_flags(self):
        inc = self.recipe.include_flags(self.arch)
        build_dir = self.recipe.get_build_dir(self.arch)
        for i in {"include/internal", "include/openssl"}:
            self.assertIn(f"-I{build_dir}/{i}", inc)

    def test_link_flags(self):
        build_dir = self.recipe.get_build_dir(self.arch)
        openssl_version = self.recipe.version
        self.assertEqual(
            f" -L{build_dir} -lcrypto{openssl_version} -lssl{openssl_version}",
            self.recipe.link_flags(self.arch),
        )

    def test_select_build_arch(self):
        expected_build_archs = {
            "armeabi": "android",
            "armeabi-v7a": "android-arm",
            "arm64-v8a": "android-arm64",
            "x86": "android-x86",
            "x86_64": "android-x86_64",
        }
        for arch in self.ctx.archs:
            self.assertEqual(
                expected_build_archs[arch.arch],
                self.recipe.select_build_arch(arch),
            )
