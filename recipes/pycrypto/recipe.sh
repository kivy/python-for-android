#!/bin/bash

VERSION_pycrypto=2.5
URL_pycrypto=http://pypi.python.org/packages/source/p/pycrypto/pycrypto-$VERSION_pycrypto.tar.gz
DEPS_pycrypto=(openssl hostpython python)
MD5_pycrypto=783e45d4a1a309e03ab378b00f97b291
BUILD_pycrypto=$BUILD_PATH/pycrypto/$(get_directory $URL_pycrypto)
RECIPE_pycrypto=$RECIPES_PATH/pycrypto

function prebuild_pycrypto() {
	true
}

function build_pycrypto() {

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/pycrypto" ]; then
		return
	fi

	cd $BUILD_pycrypto

	push_arm

	export CC="$CC -I$BUILD_openssl/include"
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$BUILD_openssl"
	export EXTRA_CFLAGS="--host linux-armv"

	try ./configure --host=arm-eabi --prefix="$BUILD_PATH/python-install" --enable-shared

	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	pop_arm
}

function postbuild_pycrypto() {
	true
}
