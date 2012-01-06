#!/bin/bash

PRIORITY_kivy=30
VERSION_kivy=
URL_kivy=
DEPS_kivy=(pygame)
MD5_kivy=
BUILD_kivy=$BUILD_PATH/kivy/kivy
RECIPE_kivy=$RECIPES_PATH/kivy

function prebuild_kivy() {
	cd $BUILD_PATH/kivy

	if [ ! -d kivy ]; then
		# initial clone
		try git clone https://github.com/kivy/kivy
		cd kivy
		try git checkout android-support
	fi
}

function build_kivy() {
	cd $BUILD_kivy

	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"

	# fake try to be able to cythonize generated files
	$BUILD_PATH/python-install/bin/python.host setup.py build_ext
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	pop_arm
}

function postbuild_kivy() {
	true
}
