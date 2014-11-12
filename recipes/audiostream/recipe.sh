#!/bin/bash

VERSION_audiostream=${VERSION_audiostream:-master}
URL_audiostream=https://github.com/kivy/audiostream/archive/$VERSION_audiostream.zip
DEPS_audiostream=(python sdl pyjnius)
MD5_audiostream=
BUILD_audiostream=$BUILD_PATH/audiostream/$(get_directory $URL_audiostream)
RECIPE_audiostream=$RECIPES_PATH/audiostream

function prebuild_audiostream() {
	cd $BUILD_audiostream
}

function shouldbuild_audiostream() {
	if [ -d "$SITEPACKAGES_PATH/audiostream" ]; then
		DO_BUILD=0
	fi
}

function build_audiostream() {
	cd $BUILD_audiostream

	push_arm

	# build python extension
	export JNI_PATH=$JNI_PATH
	export CFLAGS="$CFLAGS -I$JNI_PATH/sdl/include -I$JNI_PATH/sdl_mixer/"
	export LDFLAGS="$LDFLAGS -lm -L$LIBS_PATH"
	export AUDIOSTREAM_ROOT="$BUILD_audiostream/build/audiostream/armeabi-v7a"
	try cd $BUILD_audiostream
	$HOSTPYTHON setup.py build_ext &>/dev/null
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v
	try $HOSTPYTHON setup.py install -O2
	try cp -a audiostream/platform/android/org $JAVACLASS_PATH

	pop_arm
}

function postbuild_audiostream() {
	true
}
