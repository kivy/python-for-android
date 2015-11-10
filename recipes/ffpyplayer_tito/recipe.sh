#!/bin/bash

VERSION_ffpyplayer_tito=${VERSION_ffpyplayer_tito:-master}
URL_ffpyplayer_tito=http://github.com/tito/ffpyplayer/archive/$VERSION_ffpyplayer_tito.zip
DEPS_ffpyplayer_tito=(python ffmpeg2)
MD5_ffpyplayer_tito=
BUILD_ffpyplayer_tito=$BUILD_PATH/ffpyplayer/$(get_directory $URL_ffpyplayer_tito)
RECIPE_ffpyplayer_tito=$RECIPES_PATH/ffpyplayer

function prebuild_ffpyplayer_tito() {
	true
}

function shouldbuild_ffpyplayer_tito() {
	if [ -d "$SITEPACKAGES_PATH/ffpyplayer" ]; then
		DO_BUILD=0
	fi
}

function build_ffpyplayer_tito() {
	cd $BUILD_ffpyplayer_tito

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

function postbuild_ffpyplayer_tito() {
	true
}
