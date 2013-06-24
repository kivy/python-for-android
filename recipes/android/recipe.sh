#!/bin/bash

VERSION_android=
URL_android=
DEPS_android=(pygame)
MD5_android=
BUILD_android=$BUILD_PATH/android/android
RECIPE_android=$RECIPES_PATH/android

function prebuild_android() {
	cd $BUILD_PATH/android

	rm -rf android
	if [ ! -d android ]; then
		try cp -a $RECIPE_android/src $BUILD_android
	fi
}

function build_android() {
	cd $BUILD_android

	# if the last step have been done, avoid all
	if [ -f .done ]; then
		return
	fi
	
	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	# cythonize
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	unset LDSHARED

	touch .done
	pop_arm
}

function postbuild_android() {
	true
}
