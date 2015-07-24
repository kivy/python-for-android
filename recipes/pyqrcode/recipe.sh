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

function shouldbuild_pyqrcode() {
	# if the last step have been done, avoid all
	if [ -f "$BUILD_pyqrcode/.done" ]; then
		return
	fi
	
}

function build_pyqrcode() {
	cd $BUILD_pyqrcode

	push_arm
	try $HOSTPYTHON setup.py install -O2
	touch .done
	pop_arm
}

function postbuild_pyqrcode() {
	true
}
