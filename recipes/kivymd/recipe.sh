#!/bin/bash

# version of your package
VERSION_kivymd=

# dependencies of this recipe
DEPS_kivymd=(kivy)

# url of the package
URL_kivymd=https://github.com/kivymd/KivyMD/archive/master.zip

# md5 of the package
MD5_kivymd=

# default build path
BUILD_kivymd=$BUILD_PATH/kivymd

# default recipe path
RECIPE_kivymd=$RECIPES_PATH/kivymd/$(get_directory $URL_kivymd)

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_kivymd() {
	true
}

# function called to build the source code
function build_kivymd() {
	cd $BUILD_kivymd/master
	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

# function called after all the compile have been done
function postbuild_kivymd() {
	true
}
