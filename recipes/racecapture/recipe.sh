#!/bin/bash
VERSION_racecapture=0.1
DEPS_racecapture=(kivy android)
MD5_racecapture=
BUILD_racecapture=/home/brent/git-projects/RaceCapture_App
RECIPE_racecapture=$RECIPES_PATH/racecapture

function prebuild_racecapture() {
	true
}

function shouldbuild_racecapture() {
    echo sitepackages $SITEPACKAGES_PATH
	if [ -d "$SITEPACKAGES_PATH/racecapture" ]; then
		DO_BUILD=0
	fi
}

function build_racecapture() {
    echo liblink $LIBLINK_PATH
	cd $BUILD_racecapture

	push_arm
    
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	# fake try to be able to cythonize generated files
	$HOSTPYTHON setup.py build_ext
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $HOSTPYTHON setup.py install -O2

	unset LDSHARED
	pop_arm
}

function postbuild_racecapture() {
	true
}
