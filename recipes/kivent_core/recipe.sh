#!/bin/bash

VERSION_kivent_core=2.0.0
URL_kivent_core=https://github.com/kivy/KivEnt/archive/master.zip
MD5_kivent_core=
DEPS_kivent_core=(python kivy)
BUILD_kivent_core=$BUILD_PATH/kivent_core/master/modules/core
RECIPE_kivent_core=$RECIPES_PATH/kivent_core

function prebuild_kivent_core() {
	true
}

function build_kivent_core() {
	cd $BUILD_kivent_core

	push_arm

	export LDSHARED="$LIBLINK"
	export PYTHONPATH=$BUILD_kivy/:$PYTHONPATH
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm
}

function postbuild_kivent_core() {
	true
}
