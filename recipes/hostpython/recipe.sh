#!/bin/bash

VERSION_hostpython=2.7.2
URL_hostpython=http://python.org/ftp/python/$VERSION_hostpython/Python-$VERSION_hostpython.tar.bz2
MD5_hostpython=ba7b2f11ffdbf195ee0d111b9455a5bd

# must be generated ?
BUILD_hostpython=$BUILD_PATH/hostpython/$(get_directory $URL_hostpython)
RECIPE_hostpython=$RECIPES_PATH/hostpython

function prebuild_hostpython() {
	cd $BUILD_hostpython

	# check marker in our source build
	if [ -f .patched ]; then
		# no patch needed
		return
	fi

	try patch -p1 < $RECIPE_hostpython/patches/fix-bug-17547.patch

	# everything done, touch the marker !
	touch .patched

	try cp $RECIPE_hostpython/Setup Modules/Setup
}

function shouldbuild_hostpython() {
	cd $BUILD_hostpython
	if [ -f hostpython ]; then
		DO_BUILD=0
	fi
}

function build_hostpython() {
	# placeholder for building
	cd $BUILD_hostpython

    try ./configure
    try make -j5 -k
    try make
    try mv Parser/pgen hostpgen

	if [ -f python.exe ]; then
		try mv python.exe hostpython
	elif [ -f python ]; then
		try mv python hostpython
	else
		error "Unable to found the python executable?"
		exit 1
	fi
}

function postbuild_hostpython() {
	# placeholder for post build
	true
}
