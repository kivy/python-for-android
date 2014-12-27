#!/bin/bash

VERSION_libyaml=${VERSION_libyaml:-0.1.5}
URL_libyaml=http://pyyaml.org/download/libyaml/yaml-${VERSION_libyaml}.tar.gz
MD5_libyaml=24f6093c1e840ca5df2eb09291a1dbf1
BUILD_libyaml=$BUILD_PATH/libyaml/$(get_directory $URL_libyaml)
RECIPE_libyaml=$RECIPES_PATH/libyaml

function prebuild_libyaml() {
	true
}

function shouldbuild_libxslt() {
	if [ -f "$BUILD_libyaml/src/.libs/libyaml.a" ]; then
		DO_BUILD=0
	fi
}

function build_libyaml() {
	cd $BUILD_libyaml

	push_arm

	# using arm-linux-eabi does not create a shared library
	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-androideabi
	try make

	try cp -L $BUILD_libyaml/src/.libs/libyaml.so $LIBS_PATH

	pop_arm
}

function postbuild_libyaml() {
	true
}
