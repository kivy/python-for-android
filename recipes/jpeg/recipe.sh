#!/bin/bash

PRIORITY_jpeg=1
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
	try ndk-build V=1 jpeg
}

function postbuild_jpeg() {
	true
}
