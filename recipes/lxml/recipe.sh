#!/bin/bash

VERSION_lxml=2.3.1
URL_lxml=http://pypi.python.org/packages/source/l/lxml/lxml-$VERSION_lxml.tar.gz
DEPS_lxml=(libxml2 libxslt python)
MD5_lxml=87931fbf35df60cd71cfe7484b4b36ed
BUILD_lxml=$BUILD_PATH/lxml/$(get_directory $URL_lxml)
RECIPE_lxml=$RECIPES_PATH/lxml

function prebuild_lxml() {
	true
}

function build_lxml() {
	cd $BUILD_lxml

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/lxml" ]; then
		return
	fi

	push_arm

	export CC="$CC -I$BUILD_libxml2/include -I$BUILD_libxslt"
	export LDFLAGS="$LDFLAGS -L$BUILD_libxslt/libxslt/.libs -L$BUILD_libxslt/libexslt/.libs -L$BUILD_libxml2/.libs"

	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	pop_arm
}

function postbuild_lxml() {
	true
}
