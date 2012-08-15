#!/bin/bash

VERSION_pyasn1=2.5
URL_pyasn1=http://downloads.sourceforge.net/project/pyasn1/pyasn1/0.1.4/pyasn1-0.1.4.tar.gz
DEPS_pyasn1=()
MD5_pyasn1=
BUILD_pyasn1=$BUILD_PATH/pyasn1/$(get_directory $URL_pyasn1)
RECIPE_pyasn1=$RECIPES_PATH/pyasn1

function prebuild_pyasn1() {
	true
}

function build_pyasn1() {

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/pyasn1" ]; then
		return
	fi

	cd $BUILD_pyasn1

	push_arm

	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	pop_arm
}

function postbuild_pyasn1() {
	true
}
