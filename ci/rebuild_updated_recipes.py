#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Continuous Integration helper script.
Automatically detects recipes modified in a changeset (compares with master)
and recompiles them.

To run locally, set the environment variables before running:
```
ANDROID_SDK_HOME=~/.buildozer/android/platform/android-sdk-20
ANDROID_NDK_HOME=~/.buildozer/android/platform/android-ndk-r9c
./ci/rebuild_update_recipes.py
```

Current limitations:
- will fail on conflicting requirements
  e.g. https://travis-ci.org/AndreMiras/python-for-android/builds/438840800
  the list of recipes was huge and result was:
  [ERROR]:   Didn't find any valid dependency graphs.
  [ERROR]:   This means that some of your requirements pull in conflicting dependencies.
- only rebuilds on sdl2 bootstrap
"""
import sh
import os
import sys
import argparse
from pythonforandroid.build import Context
from pythonforandroid import logger
from pythonforandroid.toolchain import current_directory
from pythonforandroid.recipe import Recipe
from ci.constants import TargetPython, CORE_RECIPES, BROKEN_RECIPES


def modified_recipes(branch='origin/develop'):
    """
    Returns a set of modified recipes between the current branch and the one
    in param.
    """
    # using the contrib version on purpose rather than sh.git, since it comes
    # with a bunch of fixes, e.g. disabled TTY, see:
    # https://stackoverflow.com/a/20128598/185510
    git_diff = sh.contrib.git.diff('--name-only', branch)
    recipes = set()
    for file_path in git_diff:
        if 'pythonforandroid/recipes/' in file_path:
            recipe = file_path.split('/')[2]
            recipes.add(recipe)
    return recipes


def build(target_python, requirements, archs):
    """
    Builds an APK given a target Python and a set of requirements.
    """
    if not requirements:
        return
    android_sdk_home = os.environ['ANDROID_SDK_HOME']
    android_ndk_home = os.environ['ANDROID_NDK_HOME']
    requirements.add(target_python.name)
    requirements = ','.join(requirements)
    logger.info('requirements: {}'.format(requirements))

    with current_directory('testapps/on_device_unit_tests/'):
        # iterates to stream the output
        for line in sh.python(
                'setup.py', 'apk', '--sdk-dir', android_sdk_home,
                '--ndk-dir', android_ndk_home, '--requirements',
                requirements, *[f"--arch={arch}" for arch in archs],
                _err_to_out=True, _iter=True):
            print(line)


def main():
    parser = argparse.ArgumentParser("rebuild_updated_recipes")
    parser.add_argument(
        "--arch",
        help="The archs to build for during tests",
        action="append",
        default=[],
    )
    args, unknown = parser.parse_known_args(sys.argv[1:])

    logger.info(f"Building updated recipes for the following archs: {args.arch}")

    target_python = TargetPython.python3
    recipes = modified_recipes()
    logger.info('recipes modified: {}'.format(recipes))
    recipes -= CORE_RECIPES
    logger.info('recipes to build: {}'.format(recipes))
    context = Context()

    # removing the deleted recipes for the given target (if any)
    for recipe_name in recipes.copy():
        try:
            Recipe.get_recipe(recipe_name, context)
        except ValueError:
            # recipe doesn't exist, so probably we remove it
            recipes.remove(recipe_name)
            logger.warning(
                'removed {} from recipes because deleted'.format(recipe_name)
            )

    # removing the known broken recipe for the given target
    broken_recipes = BROKEN_RECIPES[target_python]
    recipes -= broken_recipes
    logger.info('recipes to build (no broken): {}'.format(recipes))
    build(target_python, recipes, args.arch)


if __name__ == '__main__':
    main()
