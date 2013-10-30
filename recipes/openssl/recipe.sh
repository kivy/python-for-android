#!/bin/bash

VERSION_openssl=${VERSION_openssl:-1.0.1c}
URL_openssl=http://www.openssl.org/source/openssl-$VERSION_openssl.tar.gz
DEPS_openssl=()
MD5_openssl=ae412727c8c15b67880aef7bd2999b2e
BUILD_openssl=$BUILD_PATH/openssl/$(get_directory $URL_openssl)
RECIPE_openssl=$RECIPES_PATH/openssl

function prebuild_openssl() {
	true
}

function shouldbuild_openssl() {
	if [ -f "$BUILD_openssl/libssl.a" ]; then
		DO_BUILD=0
	fi
}

function build_openssl() {
	cd $BUILD_openssl

	push_arm

	try ./Configure no-dso no-krb5 linux-armv4
	try make build_libs

	pop_arm
}

function postbuild_openssl() {
	true
}
