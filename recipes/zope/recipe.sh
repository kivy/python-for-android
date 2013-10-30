#!/bin/bash

VERSION_zope=${VERSION_zope:-3.8.0}
URL_zope=http://pypi.python.org/packages/source/z/zope.interface/zope.interface-$VERSION_zope.tar.gz
DEPS_zope=(python)
MD5_zope=8ab837320b4532774c9c89f030d2a389
BUILD_zope=$BUILD_PATH/zope/$(get_directory $URL_zope)
RECIPE_zope=$RECIPES_PATH/zope

function prebuild_zope() {
	true
}

function shouldbuild_zope() {
	if [ -d "$SITEPACKAGES_PATH/zope/interface" ]; then
		DO_BUILD=0
	fi
}

function build_zope() {

	cd $BUILD_zope

	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"
	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages

        try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/zope/interface/tests
	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/zope/interface/*.txt

	unset LDSHARED

	pop_arm
}

function postbuild_zope() {
	true
}

