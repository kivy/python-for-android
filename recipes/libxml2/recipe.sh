#!/bin/bash

VERSION_libxml2=${VERSION_libxml2:-2.7.8}
URL_libxml2=ftp://xmlsoft.org/libxml2/libxml2-$VERSION_libxml2.tar.gz
DEPS_libxml2=()
MD5_libxml2=8127a65e8c3b08856093099b52599c86
BUILD_libxml2=$BUILD_PATH/libxml2/$(get_directory $URL_libxml2)
RECIPE_libxml2=$RECIPES_PATH/libxml2

function prebuild_libxml2() {
	true
}

function shouldbuild_libxml2() {
	if [ -f "$BUILD_libxml2/.libs/libxml2.a" ]; then
		DO_BUILD=0
	fi
}

function build_libxml2() {
	cd $BUILD_libxml2

	push_arm

	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi \
		--without-modules --without-legacy --without-history --without-debug --without-docbook --without-python
	try $SED 's/ runtest\$(EXEEXT) \\/ \\/' Makefile
	try $SED 's/ testrecurse\$(EXEEXT)$//' Makefile
	try make

	pop_arm
}

function postbuild_libxml2() {
	true
}
