#!/bin/bash

URL_sl4acompat=https://github.com/damonkohler/sl4a/raw/dcfa832f80/android/script_for_android_template.zip
DEPS_sl4acompat=()
MD5_sl4acompat=eed6a34bdf63e57a94b3c61528b6a577
BUILD_sl4acompat=$BUILD_PATH/sl4acompat/
RECIPE_sl4acompat=$RECIPES_PATH/sl4acompat

function prebuild_sl4acompat() {
	true
}

function shouldbuild_sl4acompat() {
	true
}

function build_sl4acompat() {
        true
}

function postbuild_sl4acompat() {
        cd $BUILD_sl4acompat
        mkdir "$DIST_PATH"/libs
        cp -a libs/* "$DIST_PATH"/libs/
        cd -
	true
}
