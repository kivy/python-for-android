#!/bin/bash

VERSION_storm=${VERSION_storm:-0.20}
DEPS_storm=(python)
URL_storm=https://pypi.python.org/packages/source/s/storm/storm-$VERSION_storm.tar.bz2
MD5_storm=4a9048fed9d1ec472ce73fbe54387054
BUILD_storm=$BUILD_PATH/storm/$(get_directory $URL_storm)
RECIPE_storm=$RECIPES_PATH/storm

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_storm() {
    cd $BUILD_storm
    wget -nc http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg
    if [ -f .patched ]; then
        return
    fi
    # I still dont know how to build the c extensions for android yet.
    # Luckly, storm provides a python fallback
    try sed -i "s|BUILD_CEXTENSIONS = True|BUILD_CEXTENSIONS = False|" setup.py
    touch .patched
}

function shouldbuild_storm() {
    if [ -d "$SITEPACKAGES_PATH/storm" ]; then
        DO_BUILD=0
    fi
}

function build_storm() {
    cd $BUILD_storm
    push_arm
    try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages
    pop_arm
}

# function called after all the compile have been done
function postbuild_storm() {
    true
}

