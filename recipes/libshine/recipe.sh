#!/bin/bash

VERSION_libshine=${VERSION_libshine:-master}
URL_libshine=https://github.com/toots/shine/archive/$VERSION_libshine.zip
DEPS_libshine=()
MD5_libshine=
BUILD_libshine=$BUILD_PATH/libshine/$(get_directory $URL_libshine)
RECIPE_libshine=$RECIPES_PATH/libshine

function prebuild_libshine() {
	true
}

function shouldbuild_libshine() {
	if [ -f "$BUILD_libshine/lib/libshine.a" ]; then
		DO_BUILD=0
	fi
}

function build_libshine() {
	cd $BUILD_libshine

	push_arm

	# configure
	mkdir -p $BUILD_libshine
	make distclean

	try ./bootstrap

	try ./configure \
	  --host=arm-linux \
	  --enable-pic \
	  --disable-shared \
 	  --enable-static \
	  --prefix=$BUILD_libshine

	make clean
	try make -j$MAKE_JOBS
	try make install

	pop_arm
}

function postbuild_libshine() {
	true
}
