#!/bin/bash

VERSION_webob=${VERSION_webob:-1.4}
DEPS_webob=()
URL_webob=http://pypi.python.org/packages/source/W/WebOb/WebOb-${VERSION_webob}.tar.gz
MD5_webob=8437607c0cc00c35f658f972516ffb55
BUILD_webob=$BUILD_PATH/webob/$(get_directory $URL_webob)
RECIPE_webob=$RECIPES_PATH/webob

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_webob() {
	true
}

function shouldbuild_webob() {
    if [ -d "$SITEPACKAGES_PATH/webob" ]; then
		DO_BUILD=0
	fi
}

function build_webob() {
	cd $BUILD_webob
	push_arm
	export EXTRA_CFLAGS="--host linux-armv"
	try $HOSTPYTHON setup.py install -O2

	pop_arm
}

# function called after all the compile have been done
function postbuild_webob() {
	true
}

