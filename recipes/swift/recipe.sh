#!/bin/bash

#TODO get a release version if possible
VERSION_swift=
DEPS_swift=()
URL_swift=https://nodeload.github.com/triblerteam/libswift/zip/4123e6579309cd65a5ba3800e0b674f348c62bfb
MD5_swift=99cf78ea0b4aeb23a2439dd886f00f8f
FILENAME_swift=4123e6579309cd65a5ba3800e0b674f348c62bfb
EXTRACT_swift=$BUILD_PATH/swift/libswift-$FILENAME_swift
BUILD_swift=$BUILD_PATH/swift/swift
RECIPE_swift=$RECIPES_PATH/swift

function prebuild_swift() {
	true
}

function build_swift() {
	if [ ! -d "$BUILD_swift" ]; then
		cd $BUILD_PATH/swift
		mkdir -p swift
		unzip $PACKAGES_PATH/$FILENAME_swift
		rm -Rf swift/jni
		mv $EXTRACT_swift swift/jni

		# Use differend Android.mk to create a binary instead of a library
		cp $RECIPE_swift/extra/Android.mk swift/jni/Android.mk
	fi

	cd $BUILD_swift
	mkdir -p libs

	if [ -f "$BUILD_PATH/libs/swift" ]; then
		#return
		true
	fi

	push_arm

	#FIXME get it so you don't have to download the jni module manually
	export LDFLAGS=$LIBLINK
	try ndk-build -C $BUILD_swift/jni
	unset LDFLAGS

	#TODO find out why it's libevent.so and not libswift.so
	try cp -a $BUILD_swift/libs/$ARCH/libevent $LIBS_PATH/swift

	pop_arm
}

function postbuild_swift() {
	true
}

