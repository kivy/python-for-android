#!/bin/bash

VERSION_ffpyplayer=${VERSION_ffpyplayer:-master}
URL_ffpyplayer=http://github.com/matham/ffpyplayer/archive/$VERSION_ffpyplayer.zip
DEPS_ffpyplayer=(python ffmpeg2)
MD5_ffpyplayer=
BUILD_ffpyplayer=$BUILD_PATH/ffpyplayer/$(get_directory $URL_ffpyplayer)
RECIPE_ffpyplayer=$RECIPES_PATH/ffpyplayer

function prebuild_ffpyplayer() {
	true
}

function shouldbuild_ffpyplayer() {
	if [ -d "$SITEPACKAGES_PATH/ffpyplayer" ]; then
		DO_BUILD=0
	fi
}

function build_ffpyplayer() {
	cd $BUILD_ffpyplayer

	push_arm

	export FFMPEG_INCLUDE_DIR="$BUILD_ffmpeg2/build/ffmpeg/armeabi-v7a/include"
	export FFMPEG_LIB_DIR="$BUILD_ffmpeg2/build/ffmpeg/armeabi-v7a/lib"
	export SDL_INCLUDE_DIR="$SRC_PATH/jni/sdl/include"
	export LDFLAGS="-L$LIBS_PATH"

	$HOSTPYTHON setup.py build_ext -v
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v
	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	pop_arm
}

function postbuild_ffpyplayer() {
	true
}
