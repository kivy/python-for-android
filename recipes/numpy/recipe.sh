#!/bin/bash

VERSION_numpy=${VERSION_numpy:-1.7.1}
URL_numpy=http://pypi.python.org/packages/source/n/numpy/numpy-$VERSION_numpy.tar.gz
DEPS_numpy=(python)
MD5_numpy=0ab72b3b83528a7ae79c6df9042d61c6
BUILD_numpy=$BUILD_PATH/numpy/$(get_directory $URL_numpy)
RECIPE_numpy=$RECIPES_PATH/numpy

function prebuild_numpy() {
	cd $BUILD_numpy

	if [ -f .patched ]; then
		return
	fi

	try patch -p1 < $RECIPE_numpy/patches/fix-numpy.patch
	touch .patched
}

function shouldbuild_numpy() {
	if [ -d "$SITEPACKAGES_PATH/numpy" ]; then
		DO_BUILD=0
	fi
}

function build_numpy() {

	cd $BUILD_numpy

	push_arm

	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $HOSTPYTHON setup.py install -O2

	pop_arm
}

function postbuild_numpy() {
	true
}
