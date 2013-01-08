#!/bin/bash

VERSION_audiostream=
URL_audiostream=https://github.com/kivy/audiostream/zipball/master/audiostream.zip
DEPS_audiostream=(python sdl)
MD5_audiostream=
BUILD_audiostream=$BUILD_PATH/audiostream/audiostream
RECIPE_audiostream=$RECIPES_PATH/audiostream

function prebuild_audiostream() {
	cd $BUILD_audiostream
}

function build_audiostream() {
	cd $BUILD_audiostream

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/audiostream" ]; then
		#return
		true
	fi

	push_arm

	# build python extension
	export JNI_PATH=$JNI_PATH
	export CFLAGS="$CFLAGS -I$JNI_PATH/sdl/include -I$JNI_PATH/sdl_mixer/"
	export LDFLAGS="$LDFLAGS -lm -L$LIBS_PATH"
	export AUDIOSTREAM_ROOT="$BUILD_audiostream/build/audiostream/armeabi-v7a"
	try cd $BUILD_audiostream
	$BUILD_PATH/python-install/bin/python.host setup.py build_ext &>/dev/null
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
	try cp -a audiostream/platform/android/org $JAVACLASS_PATH

	pop_arm
}

function postbuild_audiostream() {
	true
}
