#!/bin/bash

VERSION_itsdangerous=${VERSION_itsdangerous:-master}
DEPS_itsdangerous=(python)
URL_itsdangerous=https://github.com/mitsuhiko/itsdangerous/archive/$VERSION_itsdangerous.zip
MD5_itsdangerous=
BUILD_itsdangerous=$BUILD_PATH/itsdangerous/$(get_directory $URL_itsdangerous)
RECIPE_itsdangerous=$RECIPES_PATH/itsdangerous

function prebuild_itsdangerous() {
	true
}

function shouldbuild_itsdangerous() {
	if [ -d "$SITEPACKAGES_PATH/itsdangerous" ]; then
		DO_BUILD=0
	fi
}

function build_itsdangerous() {
	cd $BUILD_itsdangerous

	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_itsdangerous() {
	true
}

