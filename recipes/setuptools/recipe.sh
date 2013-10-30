#!/bin/bash

VERSION_setuptools=${VERSION_setuptools:-0.6c11}
URL_setuptools=http://pypi.python.org/packages/source/s/setuptools/setuptools-$VERSION_setuptools.tar.gz
DEPS_setuptools=(python)
MD5_setuptools=7df2a529a074f613b509fb44feefe74e
BUILD_setuptools=$BUILD_PATH/setuptools/$(get_directory $URL_setuptools)
RECIPE_setuptools=$RECIPES_PATH/setuptools

function prebuild_setuptools() {
	true
}

function shouldbuild_setuptools() {
	if [ -d "$SITEPACKAGES_PATH/setuptools" ]; then
		DO_BUILD=0
	fi
}

function build_setuptools() {
	cd $BUILD_setuptools

	push_arm
	# build setuptools for android
        try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	# build setuptools for python-for-android
        try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_hostpython --install-lib=Lib/site-packages
	pop_arm
}

function postbuild_setuptools() {
	true
}
