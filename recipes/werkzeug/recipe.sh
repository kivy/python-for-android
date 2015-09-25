#!/bin/bash

VERSION_werkzeug=${VERSION_werkzeug:-master}
DEPS_werkzeug=(python pyopenssl)
URL_werkzeug=https://github.com/mitsuhiko/werkzeug/archive/$VERSION_werkzeug.zip
MD5_werkzeug=
BUILD_werkzeug=$BUILD_PATH/werkzeug/$(get_directory $URL_werkzeug)
RECIPE_werkzeug=$RECIPES_PATH/werkzeug

function prebuild_werkzeug() {
	true
}

function shouldbuild_werkzeug() {
	if [ -d "$SITEPACKAGES_PATH/werkzeug" ]; then
		DO_BUILD=0
	fi
}

function build_werkzeug() {
	cd $BUILD_werkzeug

	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_werkzeug() {
	true
}

