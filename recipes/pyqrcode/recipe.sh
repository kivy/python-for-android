#!/bin/bash

VERSION_pyqrcode=
URL_pyqrcode=
DEPS_pyqrcode=(pil)
MD5_pyqrcode=
BUILD_pyqrcode=$BUILD_PATH/pyqrcode/pyqrcode
RECIPE_pyqrcode=$RECIPES_PATH/pyqrcode

function prebuild_pyqrcode() {
	cd $BUILD_PATH/pyqrcode

	if [ ! -d pyqrcode ]; then
		try cp -a $RECIPE_pyqrcode/src $BUILD_pyqrcode
	fi
}

function build_pyqrcode() {
	cd $BUILD_pyqrcode

	# if the last step have been done, avoid all
	if [ -f .done ]; then
		return
	fi
	
	push_arm
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
	touch .done
	pop_arm
}

function postbuild_pyqrcode() {
	true
}
