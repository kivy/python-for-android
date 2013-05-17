#!/bin/bash

VERSION_kivy_stable=1.5.1
URL_kivy_stable=https://github.com/kivy/kivy/archive/$VERSION_kivy_stable.zip
DEPS_kivy_stable=(pygame pyjnius android)
MD5_kivy_stable=
BUILD_kivy_stable=$BUILD_PATH/kivy_stable/$VERSION_kivy_stable
RECIPE_kivy_stable=$RECIPES_PATH/kivy_stable

function prebuild_kivy_stable() {
	true
}

function build_kivy_stable() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/kivy" ]; then
		#return
		true
	fi

	cd $BUILD_kivy_stable

	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	# fake try to be able to cythonize generated files
	$BUILD_PATH/python-install/bin/python.host setup.py build_ext
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/kivy/tools

	unset LDSHARED
	pop_arm
}

function postbuild_kivy_stable() {
	true
}
 
