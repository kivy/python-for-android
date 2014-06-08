#!/bin/bash

VERSION_cjklib=${VERSION_cjklib:-0.3.2}
DEPS_cjklib=(setuptools android)
URL_cjklib=http://pypi.python.org/packages/source/c/cjklib/cjklib-${VERSION_cjklib}.tar.gz
MD5_cjklib=32780bc5cc0b132204d1c9b8a1642157
BUILD_cjklib=$BUILD_PATH/cjklib/$(get_directory $URL_cjklib)
RECIPE_cjklib=$RECIPES_PATH/cjklib

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_cjklib() {
	true
}

function shouldbuild_cjklib() {
    if [ -d "$SITEPACKAGES_PATH/cjklib" ]; then
		DO_BUILD=0
    fi
}

function build_cjklib() {
	cd $BUILD_cjklib
	push_arm
	export EXTRA_CFLAGS="--host linux-armv"
	try $HOSTPYTHON setup.py install -O2
	pop_arm
}

# function called after all the compile have been done
function postbuild_cjklib() {
	true
}

