#!/bin/bash

VERSION_paramiko=${VERSION_paramiko:-1.10.1}
DEPS_paramiko=(pycrypto python)
URL_paramiko=http://pypi.python.org/packages/source/p/paramiko/paramiko-$VERSION_paramiko.tar.gz
MD5_paramiko=4ba105e2d8535496fd633889396b20b7
BUILD_paramiko=$BUILD_PATH/paramiko/$(get_directory $URL_paramiko)
RECIPE_paramiko=$RECIPES_PATH/paramiko

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_paramiko() {
	true
}

function shouldbuild_paramiko() {
    if [ -d "$SITEPACKAGES_PATH/paramiko" ]; then
		DO_BUILD=0
	fi
}

function build_paramiko() {
	cd $BUILD_paramiko
	push_arm
	export EXTRA_CFLAGS="--host linux-armv"
	try $HOSTPYTHON setup.py install -O2
	pop_arm
}

# function called after all the compile have been done
function postbuild_paramiko() {
	true
}

