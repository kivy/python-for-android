#!/bin/bash

VERSION_gnutls=3.3.16
DEPS_gnutls=(nettle)
URL_gnutls=ftp://ftp.gnutls.org/gcrypt/gnutls/v3.3/gnutls-${VERSION_gnutls}.tar.xz
BUILD_gnutls=$BUILD_PATH/gnutls/$(get_directory $URL_gnutls)
RECIPE_gnutls=$RECIPES_PATH/gnutls

function prebuild_gnutls() {
	true
}

function build_gnutls() {
	cd $BUILD_gnutls
	bash
	push_arm
	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_gnutls/build/lib
	try make install
	pop_arm
}

function postbuild_gnutls() {
	true
}
