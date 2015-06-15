#!/bin/bash
VERSION_leveldb=${VERSION_leveldb:-1.18}
URL_leveldb=https://github.com/google/leveldb/archive/v${VERSION_leveldb}.tar.gz
DEPS_leveldb=()
BUILD_leveldb=$BUILD_PATH/leveldb/$(get_directory $URL_leveldb)
RECIPE_leveldb=$RECIPES_PATH/leveldb

function prebuild_leveldb() {
	cp $ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/$ARCH/libgnustl_shared.so $LIBS_PATH
}

function shouldbuild_leveldb() {
	if [ -d "$LIBS_PATH/libleveldb.so" ]; then
		DO_BUILD=0
	fi
}

function build_leveldb() {
	cd $BUILD_leveldb

	push_arm
	export CFLAGS="$CFLAGS -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/include/ -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/$ARCH/include/"
	export CFLAGS="$CFLAGS -fpic -shared"
	export CXXFLAGS=$CFLAGS
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDFLAGS="$LDFLAGS -lgnustl_shared"
	export LDSHARED=$LIBLINK

	# Make sure leveldb is compiled for Android and does not include versioned numbers
	export TARGET_OS=OS_ANDROID_CROSSCOMPILE
	#FIXME: Not idempotent
	try sed -i "127i\ \ \ \ \ \ \ \ PLATFORM_SHARED_VERSIONED=" build_detect_platform
	
	# Build
	try make

	# Copy the shared library
	try cp -L libleveldb.so $LIBS_PATH

	# Unset
	unset TARGET_OS
	unset LDSHARED
	pop_arm
}

function postbuild_leveldb() {
	true
}
