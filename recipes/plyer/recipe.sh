#!/bin/bash

VERSION_plyer=${VERSION_plyer:-master}
URL_plyer=https://github.com/plyer/plyer/zipball/$VERSION_plyer/plyer-$VERSION_plyer.zip
DEPS_plyer=(pyjnius android)
MD5_plyer=
BUILD_plyer=$BUILD_PATH/plyer/$(get_directory $URL_plyer)
RECIPE_plyer=$RECIPES_PATH/plyer

function prebuild_plyer() {
	true
}

function build_plyer() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/plyer" ]; then
		return
	fi

	cd $BUILD_plyer

	push_arm
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
	pop_arm
}

function postbuild_plyer() {
	true
}
