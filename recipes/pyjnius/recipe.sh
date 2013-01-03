#!/bin/bash

VERSION_pyjnius=
URL_pyjnius=https://github.com/kivy/pyjnius/zipball/master/pyjnius-master.zip
DEPS_pyjnius=(python)
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
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	unset LDSHARED
	pop_arm
}

function postbuild_pyjnius() {
	true
}
