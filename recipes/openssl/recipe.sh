#!/bin/bash

VERSION_openssl=1.0.0e
URL_openssl=http://www.openssl.org/source/openssl-$VERSION_openssl.tar.gz
DEPS_openssl=()
MD5_openssl=7040b89c4c58c7a1016c0dfa6e821c86
BUILD_openssl=$BUILD_PATH/openssl/$(get_directory $URL_openssl)
RECIPE_openssl=$RECIPES_PATH/openssl

function prebuild_openssl() {
	true
}

function build_openssl() {
	cd $BUILD_openssl

	if [ -f libssl.a ]; then
		return
	fi

	push_arm

	try ./Configure no-dso no-krb5 linux-armv4
	try make build_libs

	pop_arm
}

function postbuild_openssl() {
	true
}
