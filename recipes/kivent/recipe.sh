#!/bin/bash

VERSION_kivent=1.0.0
URL_kivent=https://github.com/Kovak/KivEnt/archive/master.zip
MD5_kivent=
DEPS_kivent=(python cymunk kivy)
BUILD_kivent=$BUILD_PATH/kivent/master/kivent/
RECIPE_kivent=$RECIPES_PATH/kivent

function prebuild_kivent() {
	true
}

function build_kivent() {
	cd $BUILD_kivent

	push_arm

	export LDSHARED="$LIBLINK"
	export PYTHONPATH=$BUILD_kivy/:$PYTHONPATH
	export PYTHONPATH=$BUILD_cymunk/cymunk/python:$PYTHONPATH
	try find . -iname '__init__.pyx' -exec $CYTHON {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm
}

function postbuild_kivent() {
	true
}
