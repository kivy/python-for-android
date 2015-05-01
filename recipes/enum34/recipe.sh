#!/bin/bash

# version of your package
VERSION_enum34=${VERSION_enum34:-1.0.4}

# dependencies of this recipe
DEPS_enum34=(python)

# url of the package
URL_enum34=https://pypi.python.org/packages/source/e/enum34/enum34-$VERSION_enum34.tar.gz

# md5 of the package
MD5_enum34=ac80f432ac9373e7d162834b264034b6

# default build path
BUILD_enum34=$BUILD_PATH/enum34/$(get_directory $URL_enum34)

# default recipe path
RECIPE_enum34=$RECIPES_PATH/enum34

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_enum34() {
	true
}

# function called to build the source code
function build_enum34() {
	cd $BUILD_enum34
    push_arm
    try $HOSTPYTHON setup.py install
    pop_arm
}

# function called after all the compile have been done
function postbuild_enum34() {
	true
}
