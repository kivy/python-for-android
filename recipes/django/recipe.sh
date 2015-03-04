#!/bin/bash

VERSION_django=${VERSION_django:-1.6.1}
DEPS_django=(sqlite3 python)
URL_django=https://pypi.python.org/packages/source/D/Django/Django-$VERSION_django.tar.gz
MD5_django=3ea7a00ea9e7a014e8a4067dd6466a1b
BUILD_django=$BUILD_PATH/django/$(get_directory $URL_django)
RECIPE_django=$RECIPES_PATH/django

function prebuild_django() {
	true
}

function shouldbuild_django() {
	if [ -d "$SITEPACKAGES_PATH/django" ]; then
		DO_BUILD=0
	fi
}

function build_django() {
	cd $BUILD_django
	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_django() {
	# ensure the blacklist doesn't contain wsgiref or unittest
	$SED '/unittest/d' $BUILD_PATH/blacklist.txt
	$SED '/wsgiref/d' $BUILD_PATH/blacklist.txt
}
