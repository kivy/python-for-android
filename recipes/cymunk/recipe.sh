#!/bin/bash

VERSION_cymunk=${VERSION_cymunk:-master}
URL_cymunk=http://github.com/tito/cymunk/zipball/$VERSION_cymunk/cymunk.zip
DEPS_cymunk=(python)
MD5_cymunk=
BUILD_cymunk=$BUILD_PATH/cymunk/$(get_directory $URL_cymunk)
RECIPE_cymunk=$RECIPES_PATH/cymunk

function prebuild_cymunk() {
	true
}

function build_cymunk() {
	cd $BUILD_cymunk

	push_arm

	export LDSHARED="$LIBLINK"

	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	if [ "X$DO_DEBUG_BUILD" == "X" ]
	then
		try find build/lib.* -name "*.o" -exec $STRIP {} \;
	fi

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm
}

function postbuild_cymunk() {
	true
}
