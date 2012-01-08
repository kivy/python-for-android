#!/bin/bash

VERSION_jpeg=
URL_jpeg=
MD5_jpeg=
BUILD_jpeg=$SRC_PATH/jni/jpeg
RECIPE_jpeg=$RECIPES_PATH/jpeg

function prebuild_jpeg() {
	true
}

function build_jpeg() {
	cd $SRC_PATH/jni
	push_arm
	try ndk-build V=1 jpeg
	pop_arm
}

function postbuild_jpeg() {
	true
}
