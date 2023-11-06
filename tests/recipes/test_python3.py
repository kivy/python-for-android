import unittest

from os.path import join
from unittest import mock

from pythonforandroid.recipes.python3 import (
    NDK_API_LOWER_THAN_SUPPORTED_MESSAGE,
)
from pythonforandroid.util import BuildInterruptingException, build_platform
from tests.recipes.recipe_lib_test import RecipeCtx


class TestPython3Recipe(RecipeCtx, unittest.TestCase):
    """
    TestCase for recipe :mod:`~pythonforandroid.recipes.python3`
    """
    recipe_name = "python3"
    expected_compiler = (
        f"/opt/android/android-ndk/toolchains/"
        f"llvm/prebuilt/{build_platform}/bin/clang"
    )

    def test_property__libpython(self):
        self.assertEqual(
            self.recipe._libpython,
            f'libpython{self.recipe.link_version}.so'
        )

    @mock.patch('pythonforandroid.recipes.python3.Path.is_file')
    def test_should_build(self, mock_is_file):
        # in case that python lib exists, we shouldn't trigger the build
        self.assertFalse(self.recipe.should_build(self.arch))
        # in case that python lib doesn't exist, we should trigger the build
        mock_is_file.return_value = False
        self.assertTrue(self.recipe.should_build(self.arch))

    def test_include_root(self):
        expected_include_dir = join(
            self.recipe.get_build_dir(self.arch.arch), 'Include',
        )
        self.assertEqual(
            expected_include_dir, self.recipe.include_root(self.arch.arch)
        )

    def test_link_root(self):
        expected_link_root = join(
            self.recipe.get_build_dir(self.arch.arch), 'android-build',
        )
        self.assertEqual(
            expected_link_root, self.recipe.link_root(self.arch.arch)
        )

    @mock.patch("pythonforandroid.recipes.python3.subprocess.call")
    def test_compile_python_files(self, mock_subprocess):
        fake_compile_dir = '/fake/compile/dir'
        hostpy = self.recipe.ctx.hostpython = '/fake/hostpython3'
        self.recipe.compile_python_files(fake_compile_dir)
        mock_subprocess.assert_called_once_with(
            [hostpy, '-OO', '-m', 'compileall', '-b', '-f', fake_compile_dir],
        )

    @mock.patch("pythonforandroid.recipe.Recipe.check_recipe_choices")
    @mock.patch("shutil.which")
    def test_get_recipe_env(
        self,
        mock_shutil_which,
        mock_check_recipe_choices,
    ):
        """
        Test that method
        :meth:`~pythonforandroid.recipes.python3.Python3Recipe.get_recipe_env`
        returns the expected flags
        """
        mock_shutil_which.return_value = self.expected_compiler
        mock_check_recipe_choices.return_value = sorted(
            self.ctx.recipe_build_order
        )
        env = self.recipe.get_recipe_env(self.arch)

        self.assertIn('-fPIC -DANDROID', env["CFLAGS"])
        self.assertEqual(env["CC"], self.arch.get_clang_exe(with_target=True))

        # make sure that the mocked methods are actually called
        mock_check_recipe_choices.assert_called()

    def test_set_libs_flags(self):
        # todo: properly check `Python3Recipe.set_lib_flags`
        pass

    # These decorators are to mock calls to `get_recipe_env`
    # and `set_libs_flags`, since these calls are tested separately
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.util.makedirs")
    @mock.patch("shutil.which")
    def test_build_arch(
            self,
            mock_shutil_which,
            mock_makedirs,
            mock_chdir):
        mock_shutil_which.return_value = self.expected_compiler

        # specific `build_arch` mocks
        with mock.patch(
                "builtins.open",
                mock.mock_open(read_data="#define ZLIB_VERSION 1.1\nfoo")
        ) as mock_open_zlib, mock.patch(
            "pythonforandroid.recipes.python3.sh.Command"
        ) as mock_sh_command, mock.patch(
            "pythonforandroid.recipes.python3.sh.make"
        ) as mock_make, mock.patch(
            "pythonforandroid.recipes.python3.sh.cp"
        ) as mock_cp:
            self.recipe.build_arch(self.arch)

        # make sure that the mocked methods are actually called
        recipe_build_dir = self.recipe.get_build_dir(self.arch.arch)
        sh_command_calls = {
            f"{recipe_build_dir}/config.guess",
            f"{recipe_build_dir}/configure",
        }
        for command in sh_command_calls:
            self.assertIn(
                mock.call(command),
                mock_sh_command.mock_calls,
            )
        mock_open_zlib.assert_called()
        self.assertEqual(mock_make.call_count, 1)
        for make_call, kw in mock_make.call_args_list:
            self.assertIn(
                f'INSTSONAME={self.recipe._libpython}', make_call
            )
        mock_cp.assert_called_with(
            "pyconfig.h", join(recipe_build_dir, 'Include'),
        )
        mock_makedirs.assert_called()
        mock_chdir.assert_called()

    def test_build_arch_wrong_ndk_api(self):
        # we check ndk_api using recipe's ctx
        self.recipe.ctx.ndk_api = 20
        with self.assertRaises(BuildInterruptingException) as e:
            self.recipe.build_arch(self.arch)
        self.assertEqual(
            e.exception.args[0],
            NDK_API_LOWER_THAN_SUPPORTED_MESSAGE.format(
                ndk_api=self.recipe.ctx.ndk_api,
                min_ndk_api=self.recipe.MIN_NDK_API,
            ),
        )
        # restore recipe's ctx or we could get failures with other test,
        # since we share `self.recipe with all the tests of the class
        self.recipe.ctx.ndk_api = self.ctx.ndk_api

    @mock.patch('shutil.copystat')
    @mock.patch('shutil.copyfile')
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.util.makedirs")
    @mock.patch("pythonforandroid.util.walk")
    @mock.patch("pythonforandroid.recipes.python3.sh.find")
    @mock.patch("pythonforandroid.recipes.python3.sh.cp")
    @mock.patch("pythonforandroid.recipes.python3.sh.zip")
    @mock.patch("pythonforandroid.recipes.python3.subprocess.call")
    def test_create_python_bundle(
            self,
            mock_subprocess,
            mock_sh_zip,
            mock_sh_cp,
            mock_sh_find,
            mock_walk,
            mock_makedirs,
            mock_chdir,
            mock_copyfile,
            mock_copystat,
    ):
        fake_compile_dir = '/fake/compile/dir'
        simulated_walk_result = [
            ["/fake_dir", ["__pycache__", "Lib"], ["README", "setup.py"]],
            ["/fake_dir/Lib", ["ctypes"], ["abc.pyc", "abc.py"]],
            ["/fake_dir/Lib/ctypes", [], ["util.pyc", "util.py"]],
        ]
        mock_walk.return_value = simulated_walk_result
        self.recipe.create_python_bundle(fake_compile_dir, self.arch)

        recipe_build_dir = self.recipe.get_build_dir(self.arch.arch)
        modules_build_dir = join(
            recipe_build_dir,
            'android-build',
            'build',
            'lib.linux{}-{}-{}'.format(
                '2' if self.recipe.version[0] == '2' else '',
                self.arch.command_prefix.split('-')[0],
                self.recipe.major_minor_version_string
            ))
        expected_sp_paths = [
            modules_build_dir,
            join(recipe_build_dir, 'Lib'),
            self.ctx.get_python_install_dir(self.arch.arch),
        ]
        for n, (sp_call, kw) in enumerate(mock_subprocess.call_args_list):
            self.assertEqual(sp_call[0][-1], expected_sp_paths[n])

        # we expect two calls to `walk_valid_filens`
        self.assertEqual(len(mock_walk.call_args_list), 2)

        mock_sh_zip.assert_called()
        mock_sh_cp.assert_called()
        mock_sh_find.assert_called()
        mock_makedirs.assert_called()
        mock_chdir.assert_called()
        mock_copyfile.assert_called()
        mock_copystat.assert_called()
