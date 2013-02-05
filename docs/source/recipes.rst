Available modules
=================

List of available recipes: android audiostream cymunk docutils ffmpeg
hostpython jpeg kivy kivy_stable libxml2 libxslt lxml mysql_connector
openssl pil png pyasn1 pycrypto pygame pyjnius pylibpd pyopenssl
pyqrcode python sdl setuptools sqlite3 twisted txws wokkel zope

The up-to-date list is available at:
https://github.com/kivy/python-for-android/tree/master/recipes

Only hostpython and python are 2 mandatory recipes, used for building
hostpython / target python libraries.


Create your own recipes
=======================

A recipe is a script that contain the "definition" of a module to compile.
The directory layout of a recipe for a <modulename> is something like::

    python-for-android/recipes/<modulename>/recipe.sh
    python-for-android/recipes/<modulename>/patches/
    python-for-android/recipes/<modulename>/patches/fix-path.patch

When building, all the recipe build must go to::

    python-for-android/build/<modulename>/<archiveroot>

For example, if you want to create a recipe for sdl, do::

    cd python-for-android/recipes
    mkdir sdl
    cp recipe.sh.tmpl sdl/recipe.sh
    sed -i 's#XXX#sdl#' sdl/recipe.sh

Then, edit the sdl/recipe.sh to adjust other information (version, url) and
complete build function.

