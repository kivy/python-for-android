import sys
import os
from argparse import ArgumentParser

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import setup_color, info_main, Colo_Fore, info
from pythonforandroid.build import Context
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.util import ensure_dir
from pythonforandroid.bootstraps.empty import bootstrap
from pythonforandroid.distribution import Distribution
from pythonforandroid.androidndk import AndroidNDK

DEFAULT_RECIPES = ["sdl2"]

class RecipeBuilder:
    def __init__(self, parsed_args):
        setup_color(True)
        self.build_dir = parsed_args.workdir
        self.init_context(parsed_args)
        self.build_recipes(
            set(parsed_args.recipes + DEFAULT_RECIPES),
            set(parsed_args.arch)
        )

    def init_context(self, parse_args):
        self.ctx = Context()
        self.ctx.save_prebuilt = True
        self.ctx.setup_dirs(self.build_dir)
        self.ctx.ndk_api = parse_args.min_api
        self.ctx.android_api = parse_args.target_api
        self.ctx.ndk_dir = "/home/tdynamos/.buildozer/android/platform/android-ndk-r25b"

    def build_recipes(self, recipes, archs):
        info_main(f"# Requested recipes: {Colo_Fore.BLUE}{recipes}")

        _recipes, _non_recipes, bootstrap = get_recipe_order_and_bootstrap(
            self.ctx, recipes
        )
        self.ctx.prepare_bootstrap(bootstrap)
        self.ctx.set_archs(archs)
        self.ctx.bootstrap.distribution = Distribution.get_distribution(
            self.ctx, name=bootstrap.name, recipes=recipes, archs=archs,
        )
        self.ctx.ndk = AndroidNDK("/home/tdynamos/.buildozer/android/platform/android-ndk-r25b")
        recipes = [Recipe.get_recipe(recipe, self.ctx) for recipe in _recipes]

        self.ctx.recipe_build_order = _recipes
        for recipe in recipes:
           recipe.download_if_necessary()

        for arch in self.ctx.archs:
            info_main("# Building all recipes for arch {}".format(arch.arch))

            info_main("# Unpacking recipes")
            for recipe in recipes:
                ensure_dir(recipe.get_build_container_dir(arch.arch))
                recipe.prepare_build_dir(arch.arch)

            info_main("# Prebuilding recipes")
            # 2) prebuild packages
            for recipe in recipes:
                info_main("Prebuilding {} for {}".format(recipe.name, arch.arch))
                recipe.prebuild_arch(arch)
                recipe.apply_patches(arch)

            info_main("# Building recipes")
            for recipe in recipes:
                info_main("Building {} for {}".format(recipe.name, arch.arch))
                if recipe.should_build(arch):
                    recipe.build_arch(arch)
                else:
                    info("{} said it is already built, skipping".format(recipe.name))
                recipe.install_libraries(arch)

if __name__ == "__main__":
    parser = ArgumentParser(description="Build and package recipes.")
    parser.add_argument('-r', '--recipes', nargs='+', help='Recipes to build.', required=True)
    parser.add_argument('-a', '--arch', nargs='+', help='Android arch(s) to build.', required=True)
    parser.add_argument('-w', '--workdir', type=str, help="Workdir for building recipes.", required=True)
    parser.add_argument('-m', '--min-api', type=int, help="Android ndk (minimum) api.", default=24)
    parser.add_argument('-t', '--target-api', type=int, help="Android target api.", default=24)
    RecipeBuilder(parser.parse_args())
