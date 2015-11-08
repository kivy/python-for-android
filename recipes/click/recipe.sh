#!/bin/bash

VERSION_click=${VERSION_click:-master}
DEPS_click=(python)
URL_click=https://github.com/mitsuhiko/click/archive/$VERSION_click.zip
MD5_click=
BUILD_click=$BUILD_PATH/click/$(get_directory $URL_click)
RECIPE_click=$RECIPES_PATH/click

function prebuild_click() {
	true
}

function shouldbuild_click() {
	if [ -d "$SITEPACKAGES_PATH/click" ]; then
		DO_BUILD=0
	fi
}

function build_click() {
	cd $BUILD_click

	push_arm
	sed -i "s/setuptools/distutils.core/g" `grep -rl "setuptools" ./setup.py`
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_click() {
	true
}

