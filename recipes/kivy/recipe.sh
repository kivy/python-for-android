#!/bin/bash

PRIORITY_kivy=30
VERSION_kivy=
URL_kivy=
DEPS_kivy=(pygame android)
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

	# if the last step have been done, avoid all
	if [ -f .done ]; then
		return
	fi
	
	push_arm

	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"

	# fake try to be able to cythonize generated files
	$BUILD_PATH/python-install/bin/python.host setup.py build_ext
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/kivy/tools

	touch .done
	pop_arm
}

function postbuild_kivy() {
	true
}
