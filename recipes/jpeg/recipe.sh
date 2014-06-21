#!/bin/bash

VERSION_jpeg=${VERSION_jpeg:-9a}
URL_jpeg=http://ijg.org/files/jpegsrc.v$VERSION_jpeg.tar.gz
MD5_jpeg=
BUILD_jpeg=$BUILD_PATH/jpeg/$(get_directory $URL_jpeg)
RECIPE_jpeg=$RECIPES_PATH/jpeg

function prebuild_jpeg() {
	true
}

function build_jpeg() {
	cd $BUILD_jpeg
	push_arm
	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi
	try make
	try cp .libs/libjpeg.a $LIBS_PATH
	pop_arm
}

function postbuild_jpeg() {
	true
}
