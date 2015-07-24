#!/bin/bash

VERSION_plyer=${VERSION_plyer:-master}
URL_plyer=https://github.com/kivy/plyer/archive/$VERSION_plyer.zip
DEPS_plyer=(pyjnius android)
MD5_plyer=
BUILD_plyer=$BUILD_PATH/plyer/$(get_directory $URL_plyer)
RECIPE_plyer=$RECIPES_PATH/plyer

function prebuild_plyer() {
	true
}

function shouldbuild_plyer() {
	if [ -d "$SITEPACKAGES_PATH/plyer" ]; then
		DO_BUILD=0
	fi
}

function build_plyer() {
	cd $BUILD_plyer

	push_arm
	try $HOSTPYTHON setup.py install -O2
	pop_arm
}

function postbuild_plyer() {
	true
}
