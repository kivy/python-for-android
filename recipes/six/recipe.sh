#!/bin/bash

# version of your package
VERSION_six=${VERSION_six:-1.9.0}

# dependencies of this recipe
DEPS_six=(python)

# url of the package
URL_six=https://pypi.python.org/packages/source/s/six/six-$VERSION_six.tar.gz

# md5 of the package
MD5_six=476881ef4012262dfc8adc645ee786c4

# default build path
BUILD_six=$BUILD_PATH/six/$(get_directory $URL_six)

# default recipe path
RECIPE_six=$RECIPES_PATH/six

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_six() {
	true
}

# function called to build the source code
function build_six() {
	cd $BUILD_six
    push_arm
    try $HOSTPYTHON setup.py install
    pop_arm
}

# function called after all the compile have been done
function postbuild_six() {
	true
}
