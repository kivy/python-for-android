import os
import pytest
import types
import unittest
import warnings
import mock
from backports import tempfile
from pythonforandroid.build import Context
from pythonforandroid.recipe import Recipe, import_recipe


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
                mock.patch('pythonforandroid.recipe.sh.touch')) as m_touch, (
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
        expected_call_args_list = [mock.call(1)] * (retry - 1)
        assert m_sleep.call_args_list == expected_call_args_list
