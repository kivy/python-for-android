#!/bin/bash

# version of your package
VERSION_zeroconf=${VERSION_zeroconf:-0.17.1}

# dependencies of this recipe
DEPS_zeroconf=(python six netifaces)

# url of the package
URL_zeroconf=https://pypi.python.org/packages/source/z/zeroconf/zeroconf-$VERSION_zeroconf.tar.gz

# md5 of the package
MD5_zeroconf=ec8a97fc803a49c96079f36a29e6133c

# default build path
BUILD_zeroconf=$BUILD_PATH/zeroconf/$(get_directory $URL_zeroconf)

# default recipe path
RECIPE_zeroconf=$RECIPES_PATH/zeroconf

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_zeroconf() {
    cd $BUILD_zeroconf
    if [ -f .patched ]; then
        return
    fi
    try patch -p1 < $RECIPE_zeroconf/patches/no_ctypes_fix.patch
    touch .patched
}

# function called to build the source code
function build_zeroconf() {
	cd $BUILD_zeroconf

    push_arm
    try $HOSTPYTHON setup.py install -O2
    pop_arm
}

# function called after all the compile have been done
function postbuild_zeroconf() {
	true
}
