#!/bin/bash

VERSION_pyasn1=${VERSION_pyasn1:-0.1.4}
URL_pyasn1=http://downloads.sourceforge.net/project/pyasn1/pyasn1/$VERSION_pyasn1/pyasn1-$VERSION_pyasn1.tar.gz
DEPS_pyasn1=(python)
MD5_pyasn1=
BUILD_pyasn1=$BUILD_PATH/pyasn1/$(get_directory $URL_pyasn1)
RECIPE_pyasn1=$RECIPES_PATH/pyasn1

function prebuild_pyasn1() {
	true
}

function shouldbuild_pyasn1() {
	if [ -d "$SITEPACKAGES_PATH/pyasn1" ]; then
		DO_BUILD=0
	fi
}

function build_pyasn1() {
	cd $BUILD_pyasn1
	push_arm
	try $HOSTPYTHON setup.py install -O2
	pop_arm
}

function postbuild_pyasn1() {
	true
}
