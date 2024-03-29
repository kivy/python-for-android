import unittest
from tests.recipes.recipe_ctx import RecipeCtx


class TestSDL2MixerRecipe(RecipeCtx, unittest.TestCase):
    """
    An unittest for recipe :mod:`~pythonforandroid.recipes.sdl2_mixer`
    """
    recipe_name = "sdl2_mixer"

    def setUp(self):
        """Setups bootstrap build_dir."""
        super().setUp()
        bootstrap = self.ctx.bootstrap
        bootstrap.build_dir = bootstrap.get_build_dir()

    def test_get_include_dirs(self):
        list_of_includes = self.recipe.get_include_dirs(self.arch)
        self.assertIsInstance(list_of_includes, list)
        self.assertTrue(list_of_includes[0].endswith("include"))
