#!/bin/bash

VERSION_sqlite3=3
URL_sqlite3=
MD5_sqlite3=
BUILD_sqlite3=$SRC_PATH/jni/sqlite3
RECIPE_sqlite3=$RECIPES_PATH/sqlite3

function prebuild_sqlite3() {
	true
}

function build_sqlite3() {
	cd $SRC_PATH/jni
	push_arm
	try ndk-build V=1 sqlite3
	pop_arm
}

function postbuild_sqlite3() {
	# ensure the blacklist doesn't contain sqlite3
	$SED '/#>sqlite3/,/#<sqlite3/d' $BUILD_PATH/blacklist.txt
}
