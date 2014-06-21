#!/bin/bash

VERSION_png=${VERSION_png:-1.6.12}
URL_png=http://downloads.sourceforge.net/project/libpng/libpng16/$VERSION_png/libpng-$VERSION_png.tar.gz
MD5_png=297388a6746a65a2127ecdeb1c6e5c82
BUILD_png=$BUILD_PATH/png/$(get_directory $URL_png)
RECIPE_png=$RECIPES_PATH/png

function prebuild_png() {
	true
}

function build_png() {
	cd $BUILD_png
	push_arm
	try cp scripts/pnglibconf.h.prebuilt pnglibconf.h
	try cp scripts/makefile.gcc makefile
	try env make CC="$CC"
	try cp libpng.a $LIBS_PATH
	pop_arm
}

function postbuild_png() {
	true
}
