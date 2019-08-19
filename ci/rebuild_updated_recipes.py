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
- supports mainly python3 with fallback to python2
"""
import sh
import os
from pythonforandroid.build import Context
from pythonforandroid import logger
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.toolchain import current_directory
from pythonforandroid.util import BuildInterruptingException
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


def build(target_python, requirements):
    """
    Builds an APK given a target Python and a set of requirements.
    """
    if not requirements:
        return
    testapp = 'setup_testapp_python2.py'
    android_sdk_home = os.environ['ANDROID_SDK_HOME']
    android_ndk_home = os.environ['ANDROID_NDK_HOME']
    if target_python == TargetPython.python3:
        testapp = 'setup_testapp_python3_sqlite_openssl.py'
    requirements.add(target_python.name)
    requirements = ','.join(requirements)
    logger.info('requirements: {}'.format(requirements))
    with current_directory('testapps/'):
        # iterates to stream the output
        for line in sh.python(
                testapp, 'apk', '--sdk-dir', android_sdk_home,
                '--ndk-dir', android_ndk_home, '--requirements',
                requirements, _err_to_out=True, _iter=True):
            print(line)


def main():
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

    # forces the default target
    recipes_and_target = recipes | set([target_python.name])
    try:
        build_order, python_modules, bs = get_recipe_order_and_bootstrap(
            context, recipes_and_target, None)
    except BuildInterruptingException:
        # fallback to python2 if default target is not compatible
        logger.info('incompatible with {}'.format(target_python.name))
        target_python = TargetPython.python2
        logger.info('falling back to {}'.format(target_python.name))
    # removing the known broken recipe for the given target
    broken_recipes = BROKEN_RECIPES[target_python]
    recipes -= broken_recipes
    logger.info('recipes to build (no broken): {}'.format(recipes))
    build(target_python, recipes)


if __name__ == '__main__':
    main()
