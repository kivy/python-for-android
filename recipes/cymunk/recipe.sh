#!/bin/bash

VERSION_cymunk=${VERSION_cymunk:-master}
URL_cymunk=http://github.com/tito/cymunk/archive/$VERSION_cymunk.zip
DEPS_cymunk=(python)
MD5_cymunk=
BUILD_cymunk=$BUILD_PATH/cymunk/$(get_directory $URL_cymunk)
RECIPE_cymunk=$RECIPES_PATH/cymunk

function prebuild_cymunk() {
	true
}

function shouldbuild_cymunk() {
	if [ -d "$SITEPACKAGES_PATH/cymunk" ]; then
		DO_BUILD=0
	fi
}

function build_cymunk() {
	cd $BUILD_cymunk

	push_arm

	export LDSHARED="$LIBLINK"

	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm
}

function postbuild_cymunk() {
	true
}
