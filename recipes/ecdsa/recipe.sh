#!/bin/bash


# version of your package
VERSION_ecdsa=${VERSION_ecdsa:-0.13}

# dependencies of this recipe
DEPS_ecdsa=(python)

# url of the package
URL_ecdsa=https://pypi.python.org/packages/source/e/ecdsa/ecdsa-$VERSION_ecdsa.tar.gz

# md5 of the package
MD5_ecdsa=1f60eda9cb5c46722856db41a3ae6670

# default build path
BUILD_ecdsa=$BUILD_PATH/ecdsa/$(get_directory $URL_ecdsa)

# default recipe path
RECIPE_ecdsa=$RECIPES_PATH/ecdsa

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_ecdsa() {
	true
}

# function called to build the source code
function build_ecdsa() {
	cd $BUILD_ecdsa
    push_arm
    try $HOSTPYTHON setup.py install
    pop_arm

}

# function called after all the compile have been done
function postbuild_ecdsa() {
	true
}
