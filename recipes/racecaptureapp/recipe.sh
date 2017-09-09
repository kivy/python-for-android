#!/bin/bash
VERSION_racecaptureapp=0.1
DEPS_racecaptureapp=(kivy android)
MD5_racecaptureapp=
BUILD_racecaptureapp=/home/brent/git-projects/RaceCapture_App
RECIPE_racecaptureapp=$RECIPES_PATH/racecaptureapp

function prebuild_racecaptureapp() {
    true
}

function shouldbuild_racecaptureapp() {
	if [ -d "$SITEPACKAGES_PATH/racecaptureapp" ]; then
		DO_BUILD=0
	fi
}

function build_racecaptureapp() {

    echo HostPython $HOSTPYTHON
    echo CythonHost $CYTHON
    echo "build racecapture app"
	cd $BUILD_racecaptureapp

	push_arm
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"

	export PYTHONPATH=$SITEPACKAGES_PATH:$BUILDLIB_PATH

    # fake try to be able to cythonize generated files
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext --inplace
#	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $HOSTPYTHON setup.py install -O2

	unset LDSHARED

	pop_arm
}

function postbuild_racecaptureapp() {
	true
}






