#!/bin/bash

VERSION_pycrypto=${VERSION_pycrypto:-2.6.1}
URL_pycrypto=http://pypi.python.org/packages/source/p/pycrypto/pycrypto-$VERSION_pycrypto.tar.gz
DEPS_pycrypto=(openssl python)
MD5_pycrypto=55a61a054aa66812daf5161a0d5d7eda
BUILD_pycrypto=$BUILD_PATH/pycrypto/$(get_directory $URL_pycrypto)
RECIPE_pycrypto=$RECIPES_PATH/pycrypto

function prebuild_pycrypto() {
	cd $BUILD_pycrypto

	# check marker in our source build
	if [ -f .patched ]; then
		# no patch needed
		return
	fi

	try patch -p1 < $RECIPE_pycrypto/patches/add_length.patch

	# everything done, touch the marker !
	touch .patched
}

function shouldbuild_pycrypto() {
	if [ -d "$SITEPACKAGES_PATH/pycrypto" ]; then
		DO_BUILD=0
	fi
}

function build_pycrypto() {
	cd $BUILD_pycrypto

	push_arm

	export CC="$CC -I$BUILD_openssl/include"
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$BUILD_openssl"
	export EXTRA_CFLAGS="--host linux-armv"

	export ac_cv_func_malloc_0_nonnull=yes
	try ./configure --host=arm-eabi --prefix="$BUILD_PATH/python-install" --enable-shared

	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	try $HOSTPYTHON setup.py install -O2

	pop_arm
}

function postbuild_pycrypto() {
	true
}
