#!/bin/bash
# This recipe was tested with the libnacl module
VERSION_libsodium=${VERSION_libsodium:-1.0.3}
URL_libsodium=https://github.com/jedisct1/libsodium/releases/download/${VERSION_libsodium}/libsodium-${VERSION_libsodium}.tar.gz
DEPS_libsodium=(python)
MD5_libsodium=b3bcc98e34d3250f55ae196822307fab
BUILD_libsodium=$BUILD_PATH/libsodium/$(get_directory $URL_libsodium)
RECIPE_libsodium=$RECIPES_PATH/libsodium

function prebuild_libsodium() {
	true
}

function shouldbuild_libsodium() {
	if [ -e "$LIBS_PATH/libsodium.so" ]; then
		DO_BUILD=0
	fi
}

function build_libsodium() {
	cd $BUILD_libsodium

	push_arm

	try ./configure --enable-minimal --disable-soname-versions --host="arm-linux-androideabi" --enable-shared
	try make -j$MAKE_JOBS

	try cp -L $BUILD_libsodium/src/libsodium/.libs/libsodium.so $LIBS_PATH

	pop_arm
}

function postbuild_libsodium() {
	true
}
