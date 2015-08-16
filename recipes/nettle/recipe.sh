#!/bin/bash

VERSION_nettle=2.7.1
URL_nettle=https://ftp.gnu.org/gnu/nettle/nettle-${VERSION_nettle}.tar.gz
BUILD_nettle=$BUILD_PATH/nettle/$(get_directory $URL_nettle)
RECIPE_nettle=$RECIPES_PATH/nettle

function prebuild_nettle() {
	true
}

function build_nettle() {
	cd $BUILD_nettle
	push_arm
	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_nettle/build/
	try make install
    	libtool --finish $BUILD_nettle/build/
	pop_arm
}

function postbuild_nettle() {
	true
}
