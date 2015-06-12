#!/bin/bash

VERSION_cherrypy=3.7.0
DEPS_cherrypy=(python)
URL_cherrypy=https://pypi.python.org/packages/source/C/CherryPy/CherryPy-$VERSION_cherrypy.tar.gz
MD5_cherrypy=fbf36f0b393aee2ebcbc71e3ec6f6832
BUILD_cherrypy=$BUILD_PATH/cherrypy/$(get_directory $URL_cherrypy)
RECIPE_cherrypy=$RECIPES_PATH/cherrypy

function prebuild_cherrypy() {
	true
}

function shouldbuild_cherrypy() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/cherrypy" ]; then
		DO_BUILD=0
	fi
}

function build_cherrypy() {
	cd $BUILD_cherrypy

	push_arm

	try $HOSTPYTHON setup.py install

	pop_arm
}

function postbuild_cherrypy() {
	true
}
