#!/bin/bash

VERSION_pyparsing=${VERSION_pyparsing:-2.0.1}
DEPS_pyparsing=(python)
URL_pyparsing=http://pypi.python.org/packages/source/p/pyparsing/pyparsing-$VERSION_pyparsing.tar.gz
MD5_pyparsing=37adec94104b98591507218bc82e7c31
BUILD_pyparsing=$BUILD_PATH/pyparsing/$(get_directory $URL_pyparsing)
RECIPE_pyparsing=$RECIPES_PATH/pyparsing

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_pyparsing() {
	true
}

function shouldbuild_pyparsing() {
    if [ -d "$SITEPACKAGES_PATH/pyparsing" ]; then
		DO_BUILD=0
	fi
}

function build_pyparsing() {
	cd $BUILD_pyparsing
	push_arm
	export EXTRA_CFLAGS="--host linux-armv"
	try $HOSTPYTHON setup.py install -O2
	pop_arm
}

# function called after all the compile have been done
function postbuild_pyparsing() {
	true
}

