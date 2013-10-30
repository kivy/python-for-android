#!/bin/bash

VERSION_txws=${VERSION_txws:-0.7}
URL_txws=http://pypi.python.org/packages/source/t/txWS/txWS-$VERSION_txws.tar.gz
DEPS_txws=(twisted)
MD5_txws=e8f5fb03c189d83b47b21176c7574126
BUILD_txws=$BUILD_PATH/txws/$(get_directory $URL_txws)
RECIPE_txws=$RECIPES_PATH/txws

function prebuild_txws() {
	true
}

function shouldbuild_txws() {
	if [ -d "$SITEPACKAGES_PATH/txws" ]; then
		DO_BUILD=0
	fi
}

function build_txws() {
	cd $BUILD_txws
	push_arm
	export PYTHONPATH=$BUILD_PATH/hostpython/Python-2.7.2/Lib/site-packages
        try $BUILD_PATH/hostpython/Python-2.7.2/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages
	pop_arm
}

function postbuild_txws() {
	true
}

