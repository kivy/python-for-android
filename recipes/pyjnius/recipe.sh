#!/bin/bash

VERSION_pyjnius=${VERSION_pyjnius:-master}
URL_pyjnius=https://github.com/kivy/pyjnius/zipball/$VERSION_pyjnius/pyjnius-$VERSION_pyjnius.zip
DEPS_pyjnius=(python sdl)
MD5_pyjnius=
BUILD_pyjnius=$BUILD_PATH/pyjnius/$(get_directory $URL_pyjnius)
RECIPE_pyjnius=$RECIPES_PATH/pyjnius

function prebuild_pyjnius() {
	true
}

function build_pyjnius() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/jnius" ]; then
		#return
		true
	fi

	cd $BUILD_pyjnius

	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	# fake try to be able to cythonize generated files
	$BUILD_PATH/python-install/bin/python.host setup.py build_ext
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	if [ "X$DO_DEBUG_BUILD" == "X" ]; then
		try find build/lib.* -name "*.o" -exec $STRIP {} \;
	fi
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
	try cp -a jnius/src/org $JAVACLASS_PATH

	unset LDSHARED
	pop_arm
}

function postbuild_pyjnius() {
	true
}
