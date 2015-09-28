#!/bin/bash

VERSION_flask=${VERSION_flask:-master}
DEPS_flask=(python werkzeug jinja2 itsdangerous click)
URL_flask=https://github.com/mitsuhiko/flask/archive/$VERSION_flask.zip
MD5_flask=
BUILD_flask=$BUILD_PATH/flask/$(get_directory $URL_flask)
RECIPE_flask=$RECIPES_PATH/flask

function prebuild_flask() {
	true
}

function shouldbuild_flask() {
	if [ -d "$SITEPACKAGES_PATH/flask" ]; then
		DO_BUILD=0
	fi
}

function build_flask() {
	cd $BUILD_flask

	push_arm
	sed -i "s/setuptools/distutils.core/g" `grep -rl "setuptools" ./setup.py`
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_flask() {
	true
}

