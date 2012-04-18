#!/bin/bash


# version of your package
VERSION_pylibpd=1.3

# dependencies of this recipe
DEPS_pylibpd=()

# url of the
URL_pylibpd=http://ticklestep.com/pylibpd.tar.gz

# md5 of the package
MD5_pylibpd=647f813726c21445c42bc2fc77a4b146

# default build path
BUILD_pylibpd=$BUILD_PATH/pylibpd/$(get_directory $URL_pylibpd)

# default recipe path
RECIPE_pylibpd=$RECIPES_PATH/pylibpd

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_pylibpd() {
	true
}

# function called to build the source code
function build_pylibpd() {
    cd $BUILD_pylibpd/python
    push_arm
    $BUILD_PATH/python-install/bin/python.host setup.py install -O2
    pop_arm
}

# function called after all the compile have been done
function postbuild_pylibpd() {
	true
}
