#!/bin/bash

VERSION_libxslt=${VERSION_libxslt:-1.1.27}
URL_libxslt=ftp://xmlsoft.org/libxml2/libxslt-$VERSION_libxslt.tar.gz
DEPS_libxslt=(libxml2)
MD5_libxslt=
BUILD_libxslt=$BUILD_PATH/libxslt/$(get_directory $URL_libxslt)
RECIPE_libxslt=$RECIPES_PATH/libxslt

function prebuild_libxslt() {
	cd $BUILD_libxslt
	if [ -f .patched ]; then
		return
	fi
	try patch -p1 < $RECIPE_libxslt/fix-dlopen.patch
	touch .patched
}

function shouldbuild_libxslt() {
	if [ -f "$BUILD_libxslt/libxslt/.libs/libxslt.a" ]; then
		DO_BUILD=0
	fi
}

function build_libxslt() {
	cd $BUILD_libxslt

	push_arm

	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi \
		--without-plugins --without-debug --without-python --without-crypto \
		--with-libxml-src=$BUILD_libxml2
	try make


	pop_arm
}

function postbuild_libxslt() {
	true
}
