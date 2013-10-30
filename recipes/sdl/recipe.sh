#!/bin/bash

VERSION_sdl=1.2.14
URL_sdl=
MD5_sdl=
DEPS_sdl=(python)
BUILD_sdl=$BUILD_PATH/sdl/SDL-$VERSION_sdl
RECIPE_sdl=$RECIPES_PATH/sdl

function prebuild_sdl() {
	true
}

function shouldbuild_sdl() {
	if [ -f "$LIBS_PATH/libsdl.so" ]; then
		DO_BUILD=0
	fi
}

function build_sdl() {
	cd $SRC_PATH/jni

	push_arm
	try ndk-build V=1
	pop_arm

	try cp -a $SRC_PATH/libs/$ARCH/*.so $LIBS_PATH
}

function postbuild_sdl() {
	true
}
