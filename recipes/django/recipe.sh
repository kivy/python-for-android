#!/bin/bash

VERSION_django=${VERSION_django:-1.8.1}
DEPS_django=(sqlite3 setuptools python)
URL_django=https://pypi.python.org/packages/source/D/Django/Django-$VERSION_django.tar.gz
MD5_django=0f0a677a2cd56b9ab7ccb1c562d70f53
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
