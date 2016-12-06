#!/bin/bash

VERSION_ffpyplayer_codecs=
URL_ffpyplayer_codecs=
DEPS_ffpyplayer_codecs=(libshine libx264)
MD5_ffpyplayer_codecs=
BUILD_ffpyplayer_codecs=$BUILD_PATH/ffpyplayer_codecs/$(get_directory $URL_ffpyplayer_codecs)
RECIPE_ffpyplayer_codecs=$RECIPES_PATH/ffpyplayer_codecs

function prebuild_ffpyplayer_codecs() {
	true
}

function build_ffpyplayer_codecs() {
	true
}

function postbuild_ffpyplayer_codecs() {
	true
}

