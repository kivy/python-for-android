#!/bin/bash

# version of your package
VERSION_astropy=0.4.4

# dependencies of this recipe
DEPS_astropy=(numpy)

# url of the package
URL_astropy=https://pypi.python.org/packages/source/a/astropy/astropy-0.4.4.tar.gz

# md5 of the package
MD5_astropy=68da956109c5968aaa8fdab8256049ba

# default build path
BUILD_astropy=$BUILD_PATH/astropy/$(get_directory $URL_astropy)

# default recipe path
RECIPE_astropy=$RECIPES_PATH/astropy

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_astropy() {
	cd $BUILD_astropy

	if [ -f .patched ]; then
		return
	fi

	try patch -p1 < $RECIPE_astropy/patches/add_numpy_include.patch
	try patch -p1 < $RECIPE_astropy/patches/lconv_fix.patch
	touch .patched
	true
}

# function called to build the source code
function build_astropy() {
	cd $BUILD_astropy
    export BUILDLIB_PATH="$BUILD_hostpython/build/lib.linux-`uname -m`-2.7/"
    export PYTHONPATH=$SITEPACKAGES_PATH:$BUILDLIB_PATH
    export NUMPY_INCLUDE_PATH="$BUILD_PATH/python-install/lib/python2.7/site-packages/numpy/core/include"
	push_arm
	try $BUILD_PATH/python-install/bin/python.host setup.py install
	pop_arm
}

# function called after all the compile have been done
function postbuild_astropy() {
	true
}
