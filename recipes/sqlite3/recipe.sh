#!/bin/bash

VERSION_sqlite3=${VERSION_sqlite3:-3080500}
URL_sqlite3=http://www.sqlite.org/2014/sqlite-autoconf-$VERSION_sqlite3.tar.gz
MD5_sqlite3=
BUILD_sqlite3=$BUILD_PATH/sqlite3/$(get_directory $URL_sqlite3)
RECIPE_sqlite3=$RECIPES_PATH/sqlite3

function prebuild_sqlite3() {
	true
}

function build_sqlite3() {
	cd $BUILD_sqlite3
	push_arm
	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi
	try make
	try cp .libs/libsqlite3.so "$LIBS_PATH"
	pop_arm
}

function postbuild_sqlite3() {
	# ensure the blacklist doesn't contain sqlite3
	$SED '/#>sqlite3/,/#<sqlite3/d' $BUILD_PATH/blacklist.txt
}
