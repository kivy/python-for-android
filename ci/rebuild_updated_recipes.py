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
CRYSTAX_NDK_HOME=~/.buildozer/crystax-ndk
./ci/rebuild_update_recipes.py
```

Current limitations:
- will fail on conflicting requirements
  e.g. https://travis-ci.org/AndreMiras/python-for-android/builds/438840800
  the list of recipes was huge and result was:
  [ERROR]:   Didn't find any valid dependency graphs.
  [ERROR]:   This means that some of your requirements pull in conflicting dependencies.
- only rebuilds on sdl2 bootstrap
- supports mainly python3crystax with fallback to python2, but no python3 support
"""
import sh
import os
from pythonforandroid.build import Context
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.toolchain import current_directory
from ci.constants import TargetPython, CORE_RECIPES, BROKEN_RECIPES


def modified_recipes(branch='origin/master'):
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
    crystax_ndk_home = os.environ['CRYSTAX_NDK_HOME']
    if target_python == TargetPython.python3crystax:
        android_ndk_home = crystax_ndk_home
        testapp = 'setup_testapp_python3.py'
    requirements.add(target_python.name)
    requirements = ','.join(requirements)
    print('requirements:', requirements)
    with current_directory('testapps/'):
        try:
            for line in sh.python(
                    testapp, 'apk', '--sdk-dir', android_sdk_home,
                    '--ndk-dir', android_ndk_home, '--bootstrap', 'sdl2', '--requirements',
                    requirements, _err_to_out=True, _iter=True):
                print(line)
        except sh.ErrorReturnCode as e:
            raise


def main():
    target_python = TargetPython.python3crystax
    recipes = modified_recipes()
    print('recipes modified:', recipes)
    recipes -= CORE_RECIPES
    print('recipes to build:', recipes)
    context = Context()
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        context, recipes, None)
    # fallback to python2 if default target is not compatible
    if target_python.name not in build_order:
        print('incompatible with {}'.format(target_python.name))
        target_python = TargetPython.python2
        print('falling back to {}'.format(target_python.name))
    # removing the known broken recipe for the given target
    broken_recipes = BROKEN_RECIPES[target_python]
    recipes -= broken_recipes
    print('recipes to build (no broken):', recipes)
    build(target_python, recipes)


if __name__ == '__main__':
    main()
