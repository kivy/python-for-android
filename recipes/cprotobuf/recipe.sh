#!/bin/bash

VERSION_cprotobuf=${VERSION_cprotobuf:-0.1.3}
URL_cprotobuf=https://pypi.python.org/packages/source/c/cprotobuf/cprotobuf-$VERSION_cprotobuf.tar.gz
DEPS_cprotobuf=(python)
MD5_cprotobuf=c2bf4083eca57f5eb5a481999ea03755
BUILD_cprotobuf=$BUILD_PATH/cprotobuf/$(get_directory $URL_cprotobuf)
RECIPE_cprotobuf=$RECIPES_PATH/cprotobuf

function prebuild_cprotobuf() {
	true
}

function shouldbuild_cprotobuf() {
	if [ -d "$SITEPACKAGES_PATH/cprotobuf" ]; then
		DO_BUILD=0
	fi
}

function build_cprotobuf() {
	cd $BUILD_cprotobuf

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

function postbuild_cprotobuf() {
	true
}
