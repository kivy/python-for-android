import os
import pytest
import types
import unittest
import warnings
from unittest import mock
from backports import tempfile

from pythonforandroid.build import Context
from pythonforandroid.recipe import Recipe, TargetPythonRecipe, import_recipe
from pythonforandroid.archs import ArchAarch_64
from pythonforandroid.bootstrap import Bootstrap
from test_bootstrap import BaseClassSetupBootstrap


def patch_logger(level):
    return mock.patch('pythonforandroid.recipe.{}'.format(level))


def patch_logger_info():
    return patch_logger('info')


def patch_logger_debug():
    return patch_logger('debug')


def patch_urlretrieve():
    return mock.patch('pythonforandroid.recipe.urlretrieve')


class DummyRecipe(Recipe):
    pass


class TestRecipe(unittest.TestCase):

    def test_recipe_dirs(self):
        """
        Trivial `recipe_dirs()` test.
        Makes sure the list is not empty and has the root directory.
        """
        ctx = Context()
        recipes_dir = Recipe.recipe_dirs(ctx)
        # by default only the root dir `recipes` directory
        self.assertEqual(len(recipes_dir), 1)
        self.assertTrue(recipes_dir[0].startswith(ctx.root_dir))

    def test_list_recipes(self):
        """
        Trivial test verifying list_recipes returns a generator with some recipes.
        """
        ctx = Context()
        recipes = Recipe.list_recipes(ctx)
        self.assertTrue(isinstance(recipes, types.GeneratorType))
        recipes = list(recipes)
        self.assertIn('python3', recipes)

    def test_get_recipe(self):
        """
        Makes sure `get_recipe()` returns a `Recipe` object when possible.
        """
        ctx = Context()
        recipe_name = 'python3'
        recipe = Recipe.get_recipe(recipe_name, ctx)
        self.assertTrue(isinstance(recipe, Recipe))
        self.assertEqual(recipe.name, recipe_name)
        recipe_name = 'does_not_exist'
        with self.assertRaises(ValueError) as e:
            Recipe.get_recipe(recipe_name, ctx)
        self.assertEqual(
            e.exception.args[0], 'Recipe does not exist: {}'.format(recipe_name))

    def test_import_recipe(self):
        """
        Verifies we can dynamically import a recipe without warnings.
        """
        p4a_root_dir = os.path.dirname(os.path.dirname(__file__))
        name = 'pythonforandroid.recipes.python3'
        pathname = os.path.join(
            *([p4a_root_dir] + name.split('.') + ['__init__.py'])
        )
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            module = import_recipe(name, pathname)
        assert module is not None
        assert recorded_warnings == []

    def test_download_if_necessary(self):
        """
        Download should happen via `Recipe.download()` only if the recipe
        specific environment variable is not set.
        """
        # download should happen as the environment variable is not set
        recipe = DummyRecipe()
        with mock.patch.object(Recipe, 'download') as m_download:
            recipe.download_if_necessary()
        assert m_download.call_args_list == [mock.call()]
        # after setting it the download should be skipped
        env_var = 'P4A_test_recipe_DIR'
        env_dict = {env_var: '1'}
        with mock.patch.object(Recipe, 'download') as m_download, mock.patch.dict(os.environ, env_dict):
            recipe.download_if_necessary()
        assert m_download.call_args_list == []

    def test_download_url_not_set(self):
        """
        Verifies that no download happens when URL is not set.
        """
        recipe = DummyRecipe()
        with patch_logger_info() as m_info:
            recipe.download()
        assert m_info.call_args_list == [
            mock.call('Skipping test_recipe download as no URL is set')]

    @staticmethod
    def get_dummy_python_recipe_for_download_tests():
        """
        Helper method for creating a test recipe used in download tests.
        """
        recipe = DummyRecipe()
        filename = 'Python-3.7.4.tgz'
        url = 'https://www.python.org/ftp/python/3.7.4/{}'.format(filename)
        recipe._url = url
        recipe.ctx = Context()
        return recipe, filename

    def test_download_url_is_set(self):
        """
        Verifies the actual download gets triggered when the URL is set.
        """
        recipe, filename = self.get_dummy_python_recipe_for_download_tests()
        url = recipe.url
        with (
                patch_logger_debug()) as m_debug, (
                mock.patch.object(Recipe, 'download_file')) as m_download_file, (
                mock.patch('pythonforandroid.recipe.touch')) as m_touch, (
                tempfile.TemporaryDirectory()) as temp_dir:
            recipe.ctx.setup_dirs(temp_dir)
            recipe.download()
        assert m_download_file.call_args_list == [mock.call(url, filename)]
        assert m_debug.call_args_list == [
            mock.call(
                'Downloading test_recipe from '
                'https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz')]
        assert m_touch.call_count == 1

    def test_download_file_scheme_https(self):
        """
        Verifies `urlretrieve()` is being called on https downloads.
        """
        recipe, filename = self.get_dummy_python_recipe_for_download_tests()
        url = recipe.url
        with (
                patch_urlretrieve()) as m_urlretrieve, (
                tempfile.TemporaryDirectory()) as temp_dir:
            recipe.ctx.setup_dirs(temp_dir)
            assert recipe.download_file(url, filename) == filename
        assert m_urlretrieve.call_args_list == [
            mock.call(url, filename, mock.ANY)
        ]

    def test_download_file_scheme_https_oserror(self):
        """
        Checks `urlretrieve()` is being retried on `OSError`.
        After a number of retries the exception is re-reaised.
        """
        recipe, filename = self.get_dummy_python_recipe_for_download_tests()
        url = recipe.url
        with (
                patch_urlretrieve()) as m_urlretrieve, (
                mock.patch('pythonforandroid.recipe.time.sleep')) as m_sleep, (
                pytest.raises(OSError)), (
                tempfile.TemporaryDirectory()) as temp_dir:
            recipe.ctx.setup_dirs(temp_dir)
            m_urlretrieve.side_effect = OSError
            assert recipe.download_file(url, filename) == filename
        retry = 5
        expected_call_args_list = [mock.call(url, filename, mock.ANY)] * retry
        assert m_urlretrieve.call_args_list == expected_call_args_list
        expected_call_args_list = [mock.call(2**i) for i in range(retry - 1)]
        assert m_sleep.call_args_list == expected_call_args_list


class TestTargetPythonRecipe(unittest.TestCase):

    def test_major_minor_version_string(self):
        """
        Test that the major_minor_version_string property returns the correct
        string.
        """
        class DummyTargetPythonRecipe(TargetPythonRecipe):
            version = '1.2.3'

        recipe = DummyTargetPythonRecipe()
        assert recipe.major_minor_version_string == '1.2'


class TestLibraryRecipe(BaseClassSetupBootstrap, unittest.TestCase):
    def setUp(self):
        """
        Initialize a Context with a Bootstrap and a Distribution to properly
        test an library recipe, to do so we reuse `BaseClassSetupBootstrap`
        """
        super().setUp()
        self.ctx.bootstrap = Bootstrap().get_bootstrap('sdl2', self.ctx)
        self.setUp_distribution_with_bootstrap(self.ctx.bootstrap)

    def test_built_libraries(self):
        """The openssl recipe is a library recipe, so it should have set the
        attribute `built_libraries`, but not the case of `pyopenssl` recipe.
        """
        recipe = Recipe.get_recipe('openssl', self.ctx)
        self.assertTrue(recipe.built_libraries)

        recipe = Recipe.get_recipe('pyopenssl', self.ctx)
        self.assertFalse(recipe.built_libraries)

    @mock.patch('pythonforandroid.recipe.exists')
    def test_should_build(self, mock_exists):
        # avoid trying to find the recipe in a non-existing storage directory
        self.ctx.storage_dir = None

        arch = ArchAarch_64(self.ctx)
        recipe = Recipe.get_recipe('openssl', self.ctx)
        recipe.ctx = self.ctx
        self.assertFalse(recipe.should_build(arch))

        mock_exists.return_value = False
        self.assertTrue(recipe.should_build(arch))

    @mock.patch('pythonforandroid.recipe.Recipe.get_libraries')
    @mock.patch('pythonforandroid.recipe.Recipe.install_libs')
    def test_install_libraries(self, mock_install_libs, mock_get_libraries):
        mock_get_libraries.return_value = {
            '/build_lib/libsample1.so',
            '/build_lib/libsample2.so',
        }
        self.ctx.recipe_build_order = [
            "hostpython3",
            "openssl",
            "python3",
            "sdl2",
            "kivy",
        ]
        arch = ArchAarch_64(self.ctx)
        recipe = Recipe.get_recipe('openssl', self.ctx)
        recipe.install_libraries(arch)
        mock_install_libs.assert_called_once_with(
            arch, *mock_get_libraries.return_value
        )


class TesSTLRecipe(BaseClassSetupBootstrap, unittest.TestCase):
    def setUp(self):
        """
        Initialize a Context with a Bootstrap and a Distribution to properly
        test a recipe which depends on android's STL library, to do so we reuse
        `BaseClassSetupBootstrap`
        """
        super().setUp()
        self.ctx.bootstrap = Bootstrap().get_bootstrap('sdl2', self.ctx)
        self.setUp_distribution_with_bootstrap(self.ctx.bootstrap)
        self.ctx.python_recipe = Recipe.get_recipe('python3', self.ctx)

    @mock.patch('shutil.which')
    @mock.patch('pythonforandroid.build.ensure_dir')
    def test_get_recipe_env_with(
        self, mock_ensure_dir, mock_shutil_which
    ):
        """
        Test that :meth:`~pythonforandroid.recipe.STLRecipe.get_recipe_env`
        returns some expected keys and values.

        .. note:: We don't check all the env variables, only those one specific
                  of :class:`~pythonforandroid.recipe.STLRecipe`, the others
                  should be tested in the proper test.
        """
        expected_compiler = (
            f"/opt/android/android-ndk/toolchains/"
            f"llvm/prebuilt/{self.ctx.ndk.host_tag}/bin/clang"
        )
        mock_shutil_which.return_value = expected_compiler

        arch = ArchAarch_64(self.ctx)
        recipe = Recipe.get_recipe('libgeos', self.ctx)
        assert recipe.need_stl_shared, True
        env = recipe.get_recipe_env(arch)
        #  check that the mocks have been called
        mock_ensure_dir.assert_called()
        mock_shutil_which.assert_called_once_with(
            expected_compiler, path=self.ctx.env['PATH']
        )
        self.assertIsInstance(env, dict)

    @mock.patch('pythonforandroid.recipe.Recipe.install_libs')
    @mock.patch('pythonforandroid.recipe.isfile')
    @mock.patch('pythonforandroid.build.ensure_dir')
    def test_install_stl_lib(
        self, mock_ensure_dir, mock_isfile, mock_install_lib
    ):
        """
        Test that :meth:`~pythonforandroid.recipe.STLRecipe.install_stl_lib`,
        calls the method :meth:`~pythonforandroid.recipe.Recipe.install_libs`
        with the proper arguments: a subclass of
        :class:`~pythonforandroid.archs.Arch` and our stl lib
        (:attr:`~pythonforandroid.recipe.STLRecipe.stl_lib_name`)
        """
        mock_isfile.return_value = False

        arch = ArchAarch_64(self.ctx)
        recipe = Recipe.get_recipe('libgeos', self.ctx)
        recipe.ctx = self.ctx
        assert recipe.need_stl_shared, True
        recipe.install_stl_lib(arch)
        mock_install_lib.assert_called_once_with(
            arch,
            os.path.join(arch.ndk_lib_dir, f"lib{recipe.stl_lib_name}.so"),
        )
        mock_ensure_dir.assert_called()

    @mock.patch('pythonforandroid.recipe.Recipe.install_stl_lib')
    def test_postarch_build(self, mock_install_stl_lib):
        arch = ArchAarch_64(self.ctx)
        recipe = Recipe.get_recipe('libgeos', self.ctx)
        assert recipe.need_stl_shared, True
        recipe.postbuild_arch(arch)
        mock_install_stl_lib.assert_called_once_with(arch)
