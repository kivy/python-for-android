#!/bin/bash

PRIORITY_sdl=15
VERSION_sdl=1.3
URL_sdl=
MD5_sdl=
BUILD_sdl=$BUILD_PATH/sdl/SDL
RECIPE_sdl=$RECIPES_PATH/sdl

function prebuild_sdl() {
	set -x
	# clone sdl repo
	if [ ! -f $BUILD_sdl ]; then
		cd $BUILD_PATH/sdl
		hg clone http://hg.libsdl.org/SDL
	fi

	# make the symlink to sdl in src directory
	cd $SRC_PATH/jni
	rm sdl
	ln -s $BUILD_sdl sdl
}

function build_sdl() {
	cd $SRC_PATH/jni
	push_arm
	ndk-build V=1
	pop_arm

	# rename libs
	cp -a $SRC_PATH/libs/$ARCH/*.so $LIBS_PATH

	# FIXME: patch jni compilation to make it work.
	cd $LIBS_PATH
	mv libsdl_image.so libSDL_image.so
	mv libsdl_image.so libSDL_image.so
	mv libsdl_main.so libSDL_main.so
	mv libsdl_mixer.so libSDL_mixer.so
	mv libsdl_ttf.so libSDL_ttf.so
}

function postbuild_sdl() {
	true
}
