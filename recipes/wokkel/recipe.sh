#!/bin/bash

VERSION_wokkel=0.7.0
URL_wokkel=http://pypi.python.org/packages/source/w/wokkel/wokkel-$VERSION_wokkel.tar.gz
DEPS_wokkel=(setuptools twisted)
MD5_wokkel=fffc7bf564cf1d7d1ccaa6c5d18d6a76
BUILD_wokkel=$BUILD_PATH/wokkel/$(get_directory $URL_wokkel)
RECIPE_wokkel=$RECIPES_PATH/wokkel

function prebuild_wokkel() {
	true
}

function build_wokkel() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/wokkel" ]; then
		return
	fi

	cd $BUILD_wokkel

	push_arm
	export PYTHONPATH=$BUILD_PATH/hostpython/Python-2.7.2/Lib/site-packages
        try $BUILD_PATH/hostpython/Python-2.7.2/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages
	pop_arm
}

function postbuild_wokkel() {
	true
}
