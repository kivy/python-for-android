#!/bin/bash

VERSION_chipmunk=
URL_chipmunk=http://chipmunk-physics.net/release/ChipmunkLatest.tgz
DEPS_chipmunk=()
MD5_chipmunk=c5fb7d1ea529a0180e32456980f8f4a7
BUILD_chipmunk=$BUILD_PATH/chipmunk/$(get_directory $URL_chipmunk)
RECIPE_chipmunk=$RECIPES_PATH/chipmunk

function prebuild_chipmunk() {
	true
}

function build_chipmunk() {
	cd $BUILD_chipmunk

	if [ -f .libs/chipmunk.a ]; then
		return
	fi

	push_arm

	try mkdir build
	try cd build
	try cmake -DBUILD_DEMOS=OFF -DBUILD_SHARED=OFF ..
	try make

	pop_arm
}

function postbuild_chipmunk() {
	true
}
