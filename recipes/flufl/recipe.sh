#!/bin/bash

VERSION_flufl=1.1.1
URL_flufl=https://pypi.python.org/packages/source/f/flufl.i18n/flufl.i18n-$VERSION_flufl.tar.gz
DEPS_flufl=(python)
MD5_flufl=f0a63f96790b847b338aac549a3724fc
BUILD_flufl=$BUILD_PATH/flufl/$(get_directory $URL_flufl)
RECIPE_flufl=$RECIPES_PATH/flufl

function prebuild_flufl() {
	true
}

function build_flufl() {
	cd $BUILD_flufl

	push_arm
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages
	pop_arm
}

function postbuild_flufl() {
	true
}
