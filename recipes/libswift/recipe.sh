#!/bin/bash

#TODO get a release version if possible
VERSION_libswift=
DEPS_libswift=()
#TODO get a version specific URL and update the md5sum
#URL_libswift=https://github.com/whirm/tgs-android/archive/master.zip
#MD5_libswift=23ce86e2bd4d213fdcf1d8c5c37a979a
URL_libswift=https://nodeload.github.com/triblerteam/libswift/zip/4123e6579309cd65a5ba3800e0b674f348c62bfb
FILENAME_libswift=4123e6579309cd65a5ba3800e0b674f348c62bfb
EXTRACT_libswift=$BUILD_PATH/libswift/libswift-$FILENAME_libswift
BUILD_libswift=$BUILD_PATH/libswift/libswift
RECIPE_libswift=$RECIPES_PATH/libswift

function prebuild_libswift() {
	true
}

function build_libswift() {
	if [ ! -d "$BUILD_libswift" ]; then
		cd $BUILD_PATH/libswift
		mkdir -p libswift
		unzip $PACKAGES_PATH/$FILENAME_libswift
		rm -Rf libswift/jni
		mv $EXTRACT_libswift libswift/jni
	fi
	cd $BUILD_libswift
	mkdir -p libs
	
	if [ -f "$BUILD_PATH/libs/libevent.so" ]; then
		#return
		true
	fi
	
	push_arm
	
	#FIXME get it so you don't have to download the jni module manually
	export LDFLAGS=$LIBLINK
	try ndk-build -C $BUILD_libswift/jni
	unset LDFLAGS

	#TODO find out why it's libevent.so and not libswift.so
	try cp -a $BUILD_libswift/libs/$ARCH/*.so $LIBS_PATH

	pop_arm
}

function postbuild_libswift() {
	true
}

