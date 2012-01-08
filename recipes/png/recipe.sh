#!/bin/bash

VERSION_png=
URL_png=
MD5_png=
BUILD_png=$SRC_PATH/jni/png
RECIPE_png=$RECIPES_PATH/png

function prebuild_png() {
	true
}

function build_png() {
	cd $SRC_PATH/jni
	push_arm
	try ndk-build V=1 png
	pop_arm
}

function postbuild_png() {
	true
}
