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
- handle the case with conflicting requirements
  e.g. https://travis-ci.org/AndreMiras/python-for-android/builds/438840800
  the list was huge and result was:
  [ERROR]:   Didn't find any valid dependency graphs.
  [ERROR]:   This means that some of your requirements pull in conflicting dependencies.
- currently only builds on target python3crystax (even though python2 is supported)
- comprehensive list of working/broken recipes is not yet known
- only rebuilds on sdl2 bootstrap
"""
import sh
import os
from enum import Enum
from pythonforandroid.toolchain import current_directory


class TargetPython(Enum):
    python2 = 0
    python3crystax = 1


# recipes that currently break the build
# a recipe could be broken for a target Python and not for the other,
# hence we're maintaining one list per Python target
BROKEN_RECIPES_PYTHON2 = set([])
BROKEN_RECIPES_PYTHON3_CRYSTAX = set([
    # not yet python3crystax compatible
    'apsw', 'atom', 'boost', 'brokenrecipe', 'cdecimal', 'cherrypy',
    'coverage',
    # https://github.com/kivy/python-for-android/issues/550
    'audiostream',
    # enum34 is not compatible with Python 3.6 standard library
    # https://stackoverflow.com/a/45716067/185510
    'enum34',
    # https://github.com/kivy/python-for-android/issues/1398
    'ifaddrs',
    # https://github.com/kivy/python-for-android/issues/1399
    'libglob',
    # cannot find -lcrystax
    'cffi',
])
BROKEN_RECIPES = {
    TargetPython.python2: BROKEN_RECIPES_PYTHON2,
    TargetPython.python3crystax: BROKEN_RECIPES_PYTHON3_CRYSTAX,
}
# recipes that are were already built
CORE_RECIPES = set([
    'pyjnius', 'kivy', 'openssl', 'requests', 'sqlite3', 'setuptools',
    'numpy', 'android',
])


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
    broken_recipes = BROKEN_RECIPES[target_python]
    recipes = recipes - (CORE_RECIPES | broken_recipes)
    print('recipes to build:', recipes)
    build(target_python, recipes)
    print(recipes)


if __name__ == '__main__':
    main()
