#!/bin/bash

VERSION_kivy=${VERSION_kivy:-stable}
URL_kivy=https://github.com/kivy/kivy/archive/$VERSION_kivy.zip
DEPS_kivy=(pygame pyjnius android)
MD5_kivy=
BUILD_kivy=$BUILD_PATH/kivy/$(get_directory $URL_kivy)
RECIPE_kivy=$RECIPES_PATH/kivy

function prebuild_kivy() {
	true
}

function shouldbuild_kivy() {
	if [ -d "$SITEPACKAGES_PATH/kivy" ]; then
		DO_BUILD=0
	fi
}

function build_kivy() {
	cd $BUILD_kivy

	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	# fake try to be able to cythonize generated files
	$HOSTPYTHON setup.py build_ext
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $HOSTPYTHON setup.py install -O2

	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/kivy/tools

	unset LDSHARED
	pop_arm
}

function postbuild_kivy() {
	true
}
