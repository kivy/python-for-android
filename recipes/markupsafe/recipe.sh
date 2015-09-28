#!/bin/bash

VERSION_markupsafe=${VERSION_markupsafe:-master}
DEPS_markupsafe=(python)
URL_markupsafe=https://github.com/mitsuhiko/markupsafe/archive/$VERSION_markupsafe.zip
MD5_markupsafe=
BUILD_markupsafe=$BUILD_PATH/markupsafe/$(get_directory $URL_markupsafe)
RECIPE_markupsafe=$RECIPES_PATH/markupsafe

function prebuild_markupsafe() {
	true
}

function shouldbuild_markupsafe() {
	if [ -d "$SITEPACKAGES_PATH/markupsafe" ]; then
		DO_BUILD=0
	fi
}

function build_markupsafe() {
	cd $BUILD_markupsafe

	push_arm	
	sed -i "s/setuptools/distutils.core/g" `grep -rl "setuptools" ./setup.py`
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_markupsafe() {
	true
}

