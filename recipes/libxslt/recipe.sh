#!/bin/bash

VERSION_libxslt=1.1.26
URL_libxslt=ftp://xmlsoft.org/libxml2/libxslt-$VERSION_libxslt.tar.gz
DEPS_libxslt=(libxml2)
MD5_libxslt=e61d0364a30146aaa3001296f853b2b9
BUILD_libxslt=$BUILD_PATH/libxslt/$(get_directory $URL_libxslt)
RECIPE_libxslt=$RECIPES_PATH/libxslt

function prebuild_libxslt() {
	true
}

function build_libxslt() {
	cd $BUILD_libxslt

	if [ -f libxslt/.libs/libxslt.a ]; then
		return
	fi

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
