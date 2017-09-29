#!/bin/bash

VERSION_libx264=${VERSION_libx264:-last_stable_x264}
URL_libx264=ftp://ftp.videolan.org/pub/x264/snapshots/$VERSION_libx264.tar.bz2
DEPS_libx264=()
MD5_libx264=
BUILD_libx264=$BUILD_PATH/libx264/$(get_directory $URL_libx264)
RECIPE_libx264=$RECIPES_PATH/libx264

function prebuild_libx264() {
	true
}

function shouldbuild_libx264() {
	if [ -f "$BUILD_libx264/lib/libx264.a" ]; then
		DO_BUILD=0
	fi
}

function build_libx264() {
	cd $BUILD_libx264

	push_arm

	# configure
	mkdir -p $BUILD_libx264
	make distclean

	try ./configure \
	  --cross-prefix=arm-linux-androideabi- \
	  --sysroot="$NDKPLATFORM" \
	  --host=arm-linux \
	  --disable-asm \
	  --disable-cli \
	  --enable-pic \
	  --disable-shared \
 	  --enable-static \
	  --prefix=$BUILD_libx264

	make clean
	try make -j$MAKE_JOBS
	try make install

	pop_arm
}

function postbuild_libx264() {
	true
}
