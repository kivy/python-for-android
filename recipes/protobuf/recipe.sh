#!/bin/bash

VERSION_protobuf=${VERSION_protobuf:-2.6.0}
URL_protobuf=https://protobuf.googlecode.com/svn/rc/protobuf-$VERSION_protobuf.tar.gz
DEPS_protobuf=(python)
MD5_protobuf=9959d86087e64524d7f91e7a5a6e4fd7
BUILD_protobuf=$BUILD_PATH/protobuf/$(get_directory $URL_protobuf)/python
RECIPE_protobuf=$RECIPES_PATH/protobuf

function prebuild_protobuf() {
	true
}

function shouldbuild_protobuf() {
	if [ -d "$SITEPACKAGES_PATH/protobuf" ]; then
		DO_BUILD=0
	fi
}

function build_protobuf() {
	cd $BUILD_protobuf

	push_arm

	try $BUILD_hostpython/hostpython setup.py build
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	pop_arm
}

function postbuild_protobuf() {
	true
}
