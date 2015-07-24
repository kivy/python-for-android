#!/bin/bash

VERSION_pyopenssl=${VERSION_pyopenssl:-0.13}
URL_pyopenssl=http://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-$VERSION_pyopenssl.tar.gz
DEPS_pyopenssl=(openssl python)
MD5_pyopenssl=767bca18a71178ca353dff9e10941929
BUILD_pyopenssl=$BUILD_PATH/pyopenssl/$(get_directory $URL_pyopenssl)
RECIPE_pyopenssl=$RECIPES_PATH/pyopenssl

function prebuild_pyopenssl() {
	cd $BUILD_pyopenssl
	if [ -f .patched ]; then
		return
	fi

	try patch -p1 < $RECIPE_pyopenssl/fix-dlfcn.patch
	touch .patched
}

function shouldbuild_pyopenssl() {
	if [ -d "$SITEPACKAGES_PATH/OpenSSL" ]; then
		DO_BUILD=0
	fi
}

function build_pyopenssl() {
	cd $BUILD_pyopenssl

	push_arm

	export CC="$CC -I$BUILD_openssl/include"
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$BUILD_openssl"

	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	try $HOSTPYTHON setup.py install -O2

	try rm -rf $SITEPACKAGES/OpenSSL/test

	pop_arm
}

function postbuild_pyopenssl() {
	true
}
