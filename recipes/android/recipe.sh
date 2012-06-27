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
	try cython android.pyx
	try cython android_sound.pyx
	try cython android_billing.pyx
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -i

	# copy files
	try cp android.so android_sound.so android_billing.so \
		$BUILD_PATH/python-install/lib/python2.7/lib-dynload/
	try cp android_mixer.py \
		$BUILD_PATH/python-install/lib/python2.7/

	unset LDSHARED

	touch .done
	pop_arm
}

function postbuild_android() {
	true
}
