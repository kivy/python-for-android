#!/bin/bash

VERSION_kivy=
URL_kivy=https://github.com/kivy/kivy/zipball/stable/kivy-stable.zip
DEPS_kivy=(pygame pyjnius android)
MD5_kivy=
BUILD_kivy=$BUILD_PATH/kivy/$(get_directory $URL_kivy)
RECIPE_kivy=$RECIPES_PATH/kivy

function prebuild_kivy() {
	true
}

function build_kivy() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/kivy" ]; then
		#return
		true
	fi

	cd $BUILD_kivy

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

function postbuild_kivy() {
	true
}
