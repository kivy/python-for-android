#!/bin/bash

PRIORITY_sdl=15
VERSION_sdl=1.3
URL_sdl=http://www.libsdl.org/tmp/SDL-$VERSION_sdl.tar.gz
MD5_sdl=7176d5f1a0f2683bf1394e0de18c74bb
BUILD_sdl=$BUILD_PATH/sdl/$(get_directory $URL_sdl)
RECIPE_sdl=$RECIPES_PATH/sdl

function prebuild_sdl() {
	# make the symlink to sdl in src directory
	cd $SRC_PATH/jni
	if [ ! -f sdl ]; then
		ln -s $BUILD_sdl sdl
	fi
}

function build_sdl() {
	cd $SRC_PATH/jni
	ndk-build V=1
}

function postbuild_sdl() {
	true
}
