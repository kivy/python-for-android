import os

from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.distribution import Distribution
from pythonforandroid.recipe import Recipe
from pythonforandroid.build import Context
from pythonforandroid.archs import ArchAarch_64


class RecipeCtx:
    """
    An base class for unit testing a recipe. This will create a context so we
    can test any recipe using this context. Implement `setUp` and `tearDown`
    methods used by unit testing.
    """

    ctx = None
    arch = None
    recipe = None

    recipe_name = ""
    "The name of the recipe to test."

    recipes = []
    """A List of recipes to pass to `Distribution.get_distribution`. Should
    contain the target recipe to test as well as a python recipe."""
    recipe_build_order = []
    """A recipe_build_order which should take into account the recipe we want
    to test as well as the possible dependant recipes"""

    def setUp(self):
        self.ctx = Context()
        self.ctx.ndk_api = 21
        self.ctx.android_api = 27
        self.ctx._sdk_dir = "/opt/android/android-sdk"
        self.ctx._ndk_dir = "/opt/android/android-ndk"
        self.ctx.setup_dirs(os.getcwd())
        self.ctx.bootstrap = Bootstrap().get_bootstrap("sdl2", self.ctx)
        self.ctx.bootstrap.distribution = Distribution.get_distribution(
            self.ctx, name="sdl2", recipes=self.recipes
        )
        self.ctx.recipe_build_order = self.recipe_build_order
        self.ctx.python_recipe = Recipe.get_recipe("python3", self.ctx)
        self.arch = ArchAarch_64(self.ctx)
        self.ctx.ndk_platform = (
            f"{self.ctx._ndk_dir}/platforms/"
            f"android-{self.ctx.ndk_api}/{self.arch.platform_dir}"
        )
        self.recipe = Recipe.get_recipe(self.recipe_name, self.ctx)

    def tearDown(self):
        self.ctx = None
