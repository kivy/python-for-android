#!/bin/bash

VERSION_m2crypto=0.21.1
DEPS_m2crypto=(openssl hostpython python)
URL_m2crypto=http://pypi.python.org/packages/source/M/M2Crypto/M2Crypto-$VERSION_m2crypto.tar.gz
MD5_m2crypto=f93d8462ff7646397a9f77a2fe602d17
BUILD_m2crypto=$BUILD_PATH/m2crypto/$(get_directory $URL_m2crypto)
RECIPE_m2crypto=$RECIPES_PATH/m2crypto

function prebuild_m2crypto() {
	true
}

function build_m2crypto() {
	cd $BUILD_m2crypto

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/m2crypto" ]; then
	#return
	true
	fi
	push_arm

	# build python extension
	export CFLAGS="$CFLAGS -I$BUILD_PATH/python-install/include/python2.7"
	export LDSHARED=$LIBLINK
	export PYTHONPATH=$BUILD_PATH/python-install/lib/python2.7/site-packages

	try $BUILD_hostpython/hostpython setup.py build_ext --openssl=$BUILD_openssl --library-dirs=$BUILD_openssl

	unset LDSHARED

	try $BUILD_hostpython/hostpython setup.py install -O2 --prefix $BUILD_PATH/python-install

	pop_arm
}

function postbuild_m2crypto() {
	true
}
