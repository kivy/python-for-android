#!/bin/bash

VERSION_netifaces=0.10.3
DEPS_netifaces=(hostpython python setuptools)
URL_netifaces=http://pypi.python.org/packages/source/n/netifaces/netifaces-$VERSION_netifaces.tar.gz
MD5_netifaces=b96913473e1dcc3c4a7c43bc15d10e26
BUILD_netifaces=$BUILD_PATH/netifaces/$(get_directory $URL_netifaces)
RECIPE_netifaces=$RECIPES_PATH/netifaces

function prebuild_netifaces() {
	true
}

function build_netifaces() {
	cd $BUILD_netifaces

	#FIXME it actually builds an egg
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/netifaces" ]; then
	#return
	true
	fi
	push_arm

	# build python extension
	export CFLAGS="$CFLAGS -I$BUILD_PATH/python-install/include/python2.7"
	export LDSHARED=$LIBLINK
	export PYTHONPATH=$BUILD_PATH/python-install/lib/python2.7/site-packages

	# resulting .so is empty but .o will be collected into libpymodules.so in final distribute.sh step
	try $BUILD_hostpython/hostpython setup.py build_ext

	unset LDSHARED

	try $BUILD_hostpython/hostpython setup.py install -O2 --prefix $BUILD_PATH/python-install

	pop_arm
}

function postbuild_netifaces() {
	true
}
