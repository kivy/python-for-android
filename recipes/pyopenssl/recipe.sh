#!/bin/bash

VERSION_pyopenssl=0.13
URL_pyopenssl=http://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-$VERSION_pyopenssl.tar.gz
DEPS_pyopenssl=(openssl python)
MD5_pyopenssl= 767bca18a71178ca353dff9e10941929
BUILD_pyopenssl=$BUILD_PATH/pyopenssl/$(get_directory $URL_pyopenssl)
RECIPE_pyopenssl=$RECIPES_PATH/pyopenssl

function prebuild_pyopenssl() {
	true
}

function build_pyopenssl() {

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/pyOpenSSL" ]; then
		return
	fi

	cd $BUILD_pyopenssl

	push_arm

	export CC="$CC -I$BUILD_openssl/include"
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$BUILD_openssl"

	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/OpenSSL/test

	pop_arm
}

function postbuild_pyopenssl() {
	true
}
