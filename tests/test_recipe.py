import types
import unittest
from pythonforandroid.build import Context
from pythonforandroid.recipe import Recipe


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
