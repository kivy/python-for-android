#!/bin/bash

VERSION_jinja2=${VERSION_jinja2:-master}
DEPS_jinja2=(python markupsafe)
URL_jinja2=https://github.com/mitsuhiko/jinja2/archive/$VERSION_jinja2.zip
MD5_jinja2=
BUILD_jinja2=$BUILD_PATH/jinja2/$(get_directory $URL_jinja2)
RECIPE_jinja2=$RECIPES_PATH/jinja2

function prebuild_jinja2() {
	true
}

function shouldbuild_jinja2() {
	if [ -d "$SITEPACKAGES_PATH/jinja2" ]; then
		DO_BUILD=0
	fi
}

function build_jinja2() {
	cd $BUILD_jinja2

	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_jinja2() {
	true
}

